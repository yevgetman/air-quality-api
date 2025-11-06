"""
Admin configuration for adapter models.
"""
from django.contrib import admin
from .models import SourceData, RawAPIResponse, AdapterStatus


@admin.register(SourceData)
class SourceDataAdmin(admin.ModelAdmin):
    list_display = ['source', 'timestamp', 'lat', 'lon', 'aqi', 'quality_level', 'distance_km', 'created_at']
    list_filter = ['source', 'quality_level', 'timestamp']
    search_fields = ['station_name', 'station_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'


@admin.register(RawAPIResponse)
class RawAPIResponseAdmin(admin.ModelAdmin):
    list_display = ['source', 'endpoint', 'status_code', 'response_time_ms', 'is_error', 'created_at']
    list_filter = ['source', 'is_error', 'status_code', 'created_at']
    search_fields = ['endpoint', 'error_message']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(AdapterStatus)
class AdapterStatusAdmin(admin.ModelAdmin):
    list_display = ['source', 'is_active', 'success_rate_display', 'consecutive_failures', 'last_success_at', 'last_failure_at']
    list_filter = ['is_active', 'last_success_at', 'last_failure_at']
    search_fields = ['source', 'status_message']
    readonly_fields = ['created_at', 'updated_at', 'success_rate']
    ordering = ['source']
    
    def success_rate_display(self, obj):
        return f"{obj.success_rate:.1f}%"
    success_rate_display.short_description = 'Success Rate'
