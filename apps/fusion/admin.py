"""
Admin configuration for fusion models.
"""
from django.contrib import admin
from .models import BlendedData, SourceWeight, FusionLog


@admin.register(BlendedData)
class BlendedDataAdmin(admin.ModelAdmin):
    list_display = ['lat', 'lon', 'current_aqi', 'category', 'source_count', 'hit_count', 'last_updated', 'cached_until']
    list_filter = ['category', 'last_updated', 'cached_until']
    search_fields = ['lat', 'lon']
    readonly_fields = ['created_at', 'updated_at', 'last_updated', 'hit_count']
    ordering = ['-last_updated']


@admin.register(SourceWeight)
class SourceWeightAdmin(admin.ModelAdmin):
    list_display = ['source_code', 'region_code', 'priority_rank', 'trust_weight', 'is_primary', 'is_active']
    list_filter = ['region_code', 'is_active', 'is_primary']
    search_fields = ['source_code', 'notes']
    ordering = ['region_code', 'priority_rank']


@admin.register(FusionLog)
class FusionLogAdmin(admin.ModelAdmin):
    list_display = ['query_lat', 'query_lon', 'result_aqi', 'fusion_method', 'execution_time_ms', 'cache_hit', 'has_error', 'created_at']
    list_filter = ['fusion_method', 'cache_hit', 'has_error', 'created_at']
    search_fields = ['error_message']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
