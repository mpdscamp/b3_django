import yfinance as yf
from decimal import Decimal
import numpy as np
from .models import AssetPrice
import time
from requests.exceptions import RequestException, Timeout
import logging

logger = logging.getLogger(__name__)

def fetch_with_retry(ticker: str, max_retries: int = 3, timeout: int = 10, retry_delay: int = 5) -> Decimal:
    """
    Fetch price with retry logic and timeout handling.
    
    Args:
        ticker: The stock ticker symbol
        max_retries: Maximum number of retry attempts
        timeout: Timeout in seconds for each attempt
        retry_delay: Delay in seconds between retries
    
    Returns:
        Decimal: The fetched price or 0 if all attempts fail
    """
    for attempt in range(max_retries):
        try:
            # Download data with timeout
            data = yf.download(
                tickers=ticker,
                period='1d',
                interval='1m',
                timeout=timeout
            )
            
            # Check if data is empty
            if len(data) == 0:
                logger.warning(f"No data received for {ticker} (Attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue

            # Get the last close price
            last_close = data['Close'].iloc[-1]
            
            # Check if the value is NaN
            if isinstance(last_close, float) and np.isnan(last_close):
                logger.warning(f"NaN value received for {ticker} (Attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue
                
            # Format the price and return
            price_str = f"{float(last_close):.2f}"
            return Decimal(price_str)
            
        except Timeout as e:
            logger.warning(f"Timeout while fetching price for {ticker} (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue
            
        except RequestException as e:
            logger.warning(f"Network error while fetching price for {ticker} (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue
            
        except Exception as e:
            logger.error(f"Unexpected error fetching price for {ticker} (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue
    
    logger.error(f"All attempts failed for {ticker} after {max_retries} retries")
    return Decimal('0')

def fetch_latest_price(ticker: str) -> Decimal:
    """
    Main function to fetch the latest stock price.
    Example ticker for B3: 'PETR4.SA'
    """
    return fetch_with_retry(ticker)

def save_price(asset, price_value: Decimal):
    """
    Save the fetched price to AssetPrice model.
    """
    # Only save if we got a valid price
    if price_value > 0:
        try:
            AssetPrice.objects.create(asset=asset, price=price_value)
            logger.info(f"Saved price {price_value} for {asset.available_asset.ticker}")
        except Exception as e:
            logger.error(f"Error saving price for {asset.available_asset.ticker}: {str(e)}")
            raise