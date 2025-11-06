"""
Admin configuration for forecast models.
"""
from django.contrib import admin
from .models import ForecastData, AggregatedForecast


@admin.register(ForecastData)
class ForecastDataAdmin(admin.ModelAdmin):
    list_display = ['lat', 'lon', 'forecast_timestamp', 'aqi', 'category', 'source', 'generated_at']
    list_filter = ['source', 'category', 'confidence_level', 'forecast_timestamp']
    search_fields = ['lat', 'lon']
    readonly_fields = ['created_at', 'updated_at', 'generated_at']
    ordering = ['forecast_timestamp']
    date_hierarchy = 'forecast_timestamp'


@admin.register(AggregatedForecast)
class AggregatedForecastAdmin(admin.ModelAdmin):
    list_display = ['lat', 'lon', 'forecast_timestamp', 'aqi', 'category', 'source_count', 'cached_until']
    list_filter = ['category', 'forecast_timestamp', 'cached_until']
    search_fields = ['lat', 'lon']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['forecast_timestamp']
