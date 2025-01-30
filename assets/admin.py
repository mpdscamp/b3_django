# assets/admin.py

from django.contrib import admin
from .models import Asset, PriceTunnel, Frequency, AssetPrice, AvailableAsset

@admin.register(AvailableAsset)
class AvailableAssetAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name')
    search_fields = ('ticker', 'name')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('get_ticker', 'get_name')
    search_fields = ('available_asset__ticker', 'available_asset__name')
    list_filter = ('available_asset',)

    def get_ticker(self, obj):
        return obj.available_asset.ticker
    get_ticker.short_description = 'Ticker'

    def get_name(self, obj):
        return obj.available_asset.name
    get_name.short_description = 'Name'

@admin.register(PriceTunnel)
class PriceTunnelAdmin(admin.ModelAdmin):
    list_display = ('get_asset_ticker', 'lower_limit', 'upper_limit')
    search_fields = ('asset__available_asset__ticker',)

    def get_asset_ticker(self, obj):
        return obj.asset.available_asset.ticker
    get_asset_ticker.short_description = 'Asset Ticker'

@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    list_display = ('get_asset_ticker', 'interval_minutes', 'last_run')
    search_fields = ('asset__available_asset__ticker',)

    def get_asset_ticker(self, obj):
        return obj.asset.available_asset.ticker
    get_asset_ticker.short_description = 'Asset Ticker'

@admin.register(AssetPrice)
class AssetPriceAdmin(admin.ModelAdmin):
    list_display = ('get_asset_ticker', 'price', 'timestamp')
    ordering = ('-timestamp',)
    search_fields = ('asset__available_asset__ticker',)

    def get_asset_ticker(self, obj):
        return obj.asset.available_asset.ticker
    get_asset_ticker.short_description = 'Asset Ticker'
