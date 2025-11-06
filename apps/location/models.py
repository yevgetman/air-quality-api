"""
Models for location resolution and caching.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class LocationCache(TimeStampedModel):
    """
    Cache for reverse geocoding results to minimize external API calls.
    """
    # Coordinates (rounded for cache key)
    lat = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    
    # Location information
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)  # State/Province
    country = models.CharField(max_length=2, db_index=True)  # ISO country code
    zip_code = models.CharField(max_length=20, blank=True)
    formatted_address = models.TextField(blank=True)
    
    # Cache metadata
    cached_at = models.DateTimeField(auto_now=True, db_index=True)
    hit_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Location Cache'
        verbose_name_plural = 'Location Cache Entries'
        unique_together = [['lat', 'lon']]
        indexes = [
            models.Index(fields=['lat', 'lon']),
            models.Index(fields=['country']),
            models.Index(fields=['cached_at']),
        ]

    def __str__(self):
        return f"{self.city}, {self.region}, {self.country} ({self.lat}, {self.lon})"

    def increment_hit_count(self):
        """Increment cache hit counter."""
        self.hit_count += 1
        self.save(update_fields=['hit_count'])


class RegionConfig(models.Model):
    """
    Configuration for region-specific settings and data source priorities.
    """
    country_code = models.CharField(max_length=2, unique=True, db_index=True)
    country_name = models.CharField(max_length=100)
    
    # Data source priority (JSON array of source codes in order)
    source_priority = models.JSONField(default=list)
    
    # Regional settings
    default_aqi_scale = models.CharField(
        max_length=10,
        choices=[('EPA', 'EPA AQI'), ('AQHI', 'AQHI')],
        default='EPA'
    )
    
    # Coverage flags
    has_official_data = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Region Configuration'
        verbose_name_plural = 'Region Configurations'
        ordering = ['country_name']

    def __str__(self):
        return f"{self.country_name} ({self.country_code})"
