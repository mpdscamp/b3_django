# assets/tasks.py

from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

from celery import shared_task

from .models import Asset, PriceTunnel
from .price_fetcher import fetch_latest_price, save_price

logger = logging.getLogger(__name__)

@shared_task
def fetch_asset_prices():
    """
    Celery task that fetches prices for assets based on their individual frequencies.
    """
    assets = Asset.objects.select_related(
        'available_asset', 
        'price_tunnel',
        'frequency'
    ).all()
    
    current_time = timezone.now()
    
    for asset in assets:
        try:
            frequency = asset.frequency
            
            # Skip if frequency is not set
            if not frequency:
                logger.warning(f"No frequency set for {asset.available_asset.ticker}")
                continue
                
            # If last_run is None, it's the first run
            if frequency.last_run is None:
                should_run = True
            else:
                # Calculate time since last run
                time_elapsed = current_time - frequency.last_run
                should_run = time_elapsed >= timedelta(minutes=frequency.interval_minutes)
            
            if should_run:
                ticker = asset.available_asset.ticker
                logger.info(f"Fetching price for {ticker} (Frequency: {frequency.interval_minutes}min)")
                
                latest_price = fetch_latest_price(ticker)
                
                if latest_price > 0:
                    logger.info(f"Fetched price for {ticker}: {latest_price}")
                    save_price(asset, latest_price)
                    check_tunnel_and_notify(asset, latest_price)
                    
                    # Update last_run timestamp
                    frequency.last_run = current_time
                    frequency.save()
                else:
                    logger.warning(f"No valid price received for {ticker}")
            else:
                logger.debug(
                    f"Skipping {asset.available_asset.ticker} - "
                    f"Next run in {((frequency.last_run + timedelta(minutes=frequency.interval_minutes)) - current_time).seconds // 60} minutes"
                )
                
        except Exception as e:
            logger.error(f"Error processing asset {asset.available_asset.ticker}: {str(e)}")

def check_tunnel_and_notify(asset, latest_price: Decimal):
    try:
        tunnel = asset.price_tunnel
        if tunnel is None:
            logger.warning(f"No price tunnel set for {asset.available_asset.ticker}")
            return

        if latest_price < tunnel.lower_limit:
            logger.info(f"Price {latest_price} below lower limit {tunnel.lower_limit} for {asset.available_asset.ticker}")
            send_trade_email(asset, latest_price, 'BUY')
        elif latest_price > tunnel.upper_limit:
            logger.info(f"Price {latest_price} above upper limit {tunnel.upper_limit} for {asset.available_asset.ticker}")
            send_trade_email(asset, latest_price, 'SELL')

    except Exception as e:
        logger.error(f"Error in check_tunnel_and_notify for {asset.available_asset.ticker}: {str(e)}")

def send_trade_email(asset: Asset, price: Decimal, suggestion: str):
    try:
        user_email = asset.user.email
        if not user_email:
            logger.error(f"No email address set for user {asset.user.username}")
            return

        threshold = asset.price_tunnel.upper_limit if suggestion == 'SELL' else asset.price_tunnel.lower_limit

        subject = f"[B3 Monitor] {asset.available_asset.ticker}: {suggestion} Suggestion"
        message = (
            f"The latest price for {asset.available_asset.ticker} is {price}.\n"
            f"This crosses your configured threshold for {suggestion}, which is {threshold}.\n"
            f"Time: {timezone.now()}"
        )

        logger.info(f"Attempting to send email:\nFrom: {settings.DEFAULT_FROM_EMAIL}\nTo: {user_email}\nSubject: {subject}")

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # Use DEFAULT_FROM_EMAIL here
                [user_email],
                fail_silently=False
            )
            logger.info(f"Successfully sent {suggestion} email for {asset.available_asset.ticker} to {user_email}")
        except Exception as mail_error:
            logger.error(f"SMTP Error sending mail: {str(mail_error)}")
            # Print more detailed error information
            import traceback
            logger.error(f"Detailed error:\n{traceback.format_exc()}")
            raise

    except Exception as e:
        logger.error(f"Error in send_trade_email for {asset.available_asset.ticker}: {str(e)}")
        raise