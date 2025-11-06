"""
Admin configuration for location models.
"""
from django.contrib import admin
from .models import LocationCache, RegionConfig


@admin.register(LocationCache)
class LocationCacheAdmin(admin.ModelAdmin):
    list_display = ['lat', 'lon', 'city', 'region', 'country', 'hit_count', 'cached_at']
    list_filter = ['country', 'cached_at']
    search_fields = ['city', 'region', 'zip_code']
    readonly_fields = ['created_at', 'updated_at', 'cached_at', 'hit_count']
    ordering = ['-cached_at']


@admin.register(RegionConfig)
class RegionConfigAdmin(admin.ModelAdmin):
    list_display = ['country_code', 'country_name', 'default_aqi_scale', 'has_official_data', 'is_active']
    list_filter = ['default_aqi_scale', 'has_official_data', 'is_active']
    search_fields = ['country_code', 'country_name']
    ordering = ['country_name']
