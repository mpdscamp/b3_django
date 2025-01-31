from django.conf import settings
from django.db import models
from django.utils import timezone
from decimal import Decimal

class AvailableAsset(models.Model):
    """
    A master list of B3 assets (tickers) for users to choose from.
    Example: 'PETR4.SA', 'VALE3.SA', etc.
    """
    ticker = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.ticker} - {self.name}"

class Asset(models.Model):
    """
    User-chosen asset tied to a master list of available assets (AvailableAsset).
    """
    available_asset = models.ForeignKey(
        'AvailableAsset',
        on_delete=models.CASCADE,
        related_name='user_assets'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assets'
    )

    def __str__(self):
        return f"{self.user.username} tracks {self.available_asset.ticker}"

class PriceTunnel(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='price_tunnel')
    lower_limit = models.DecimalField(max_digits=10, decimal_places=2)
    upper_limit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.asset.available_asset.ticker} ({self.lower_limit} - {self.upper_limit})"

class Frequency(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='frequency')
    interval_minutes = models.PositiveIntegerField(default=5)
    last_run = models.DateTimeField(null=True, blank=True)  # Track last fetch time

    def __str__(self):
        return f"{self.asset.available_asset.ticker} every {self.interval_minutes} min"

class AssetPrice(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.asset.available_asset.ticker} - {self.price} at {self.timestamp}"
