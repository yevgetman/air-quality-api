"""
Models for storing data from various air quality sources.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class SourceData(TimeStampedModel):
    """
    Normalized air quality data from any source.
    """
    QUALITY_LEVELS = [
        ('verified', 'Verified Station Data'),
        ('model', 'Atmospheric Model'),
        ('sensor', 'Community Sensor'),
        ('estimated', 'Estimated/Interpolated'),
    ]

    # Source identification
    source = models.CharField(max_length=50, db_index=True)
    
    # Location
    lat = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    
    # Data timestamp (when the measurement was taken)
    timestamp = models.DateTimeField(db_index=True)
    
    # Air Quality Index
    aqi = models.IntegerField(null=True, blank=True)
    aqi_category = models.CharField(max_length=50, blank=True)
    
    # Pollutant concentrations
    pollutants = models.JSONField(default=dict)  # {pm25, pm10, o3, no2, so2, co}
    
    # Metadata
    quality_level = models.CharField(max_length=20, choices=QUALITY_LEVELS)
    distance_km = models.FloatField(null=True, blank=True)  # Distance from query point
    confidence_score = models.FloatField(null=True, blank=True)  # 0-100
    
    # Additional data
    station_id = models.CharField(max_length=100, blank=True)
    station_name = models.CharField(max_length=200, blank=True)
    
    class Meta:
        verbose_name = 'Source Data'
        verbose_name_plural = 'Source Data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['source', 'timestamp']),
            models.Index(fields=['lat', 'lon', 'timestamp']),
            models.Index(fields=['quality_level']),
        ]

    def __str__(self):
        return f"{self.source} - AQI:{self.aqi} at ({self.lat}, {self.lon}) - {self.timestamp}"


class RawAPIResponse(TimeStampedModel):
    """
    Store raw API responses for debugging and audit trail.
    """
    source = models.CharField(max_length=50, db_index=True)
    endpoint = models.CharField(max_length=200)
    
    # Request details
    params = models.JSONField(default=dict)
    
    # Response details
    response_data = models.JSONField()
    status_code = models.IntegerField()
    response_time_ms = models.IntegerField(null=True)  # Response time in milliseconds
    
    # Error tracking
    is_error = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Raw API Response'
        verbose_name_plural = 'Raw API Responses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source', '-created_at']),
            models.Index(fields=['is_error']),
        ]

    def __str__(self):
        return f"{self.source} - {self.endpoint} [{self.status_code}] - {self.created_at}"


class AdapterStatus(models.Model):
    """
    Track the health and status of each data source adapter.
    """
    source = models.CharField(max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    
    # Health metrics
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    consecutive_failures = models.IntegerField(default=0)
    total_requests = models.IntegerField(default=0)
    total_failures = models.IntegerField(default=0)
    
    # Rate limiting
    requests_this_minute = models.IntegerField(default=0)
    minute_window_start = models.DateTimeField(null=True, blank=True)
    
    # Status
    status_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Adapter Status'
        verbose_name_plural = 'Adapter Statuses'
        ordering = ['source']

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.source} - {status}"
    
    @property
    def success_rate(self):
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 0
        return ((self.total_requests - self.total_failures) / self.total_requests) * 100
    
    @property
    def is_healthy(self):
        """Check if adapter is considered healthy."""
        return (
            self.is_active and 
            self.consecutive_failures < 5 and 
            self.success_rate > 80
        )
