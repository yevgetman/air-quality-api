"""
Models for data fusion and blending.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class BlendedData(TimeStampedModel):
    """
    Final blended air quality data result.
    Cached for performance.
    """
    # Location
    lat = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    
    # Current air quality
    current_aqi = models.IntegerField()
    category = models.CharField(max_length=50)
    
    # Pollutant concentrations (blended values)
    pollutants = models.JSONField(default=dict)
    
    # Metadata
    sources = models.JSONField(default=list)  # List of source codes used
    source_count = models.IntegerField(default=0)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    cached_until = models.DateTimeField(db_index=True)
    
    # Cache stats
    hit_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Blended Data'
        verbose_name_plural = 'Blended Data'
        unique_together = [['lat', 'lon']]
        indexes = [
            models.Index(fields=['lat', 'lon']),
            models.Index(fields=['cached_until']),
            models.Index(fields=['-last_updated']),
        ]

    def __str__(self):
        return f"AQI {self.current_aqi} at ({self.lat}, {self.lon}) - {self.category}"
    
    def increment_hit_count(self):
        """Increment cache hit counter."""
        self.hit_count += 1
        self.save(update_fields=['hit_count'])


class SourceWeight(models.Model):
    """
    Configurable weights for each data source.
    Can be customized per region.
    """
    source_code = models.CharField(max_length=50, db_index=True)
    region_code = models.CharField(max_length=10, default='DEFAULT', db_index=True)
    
    # Weights
    trust_weight = models.FloatField(default=1.0)  # Base trust level
    priority_rank = models.IntegerField(default=5)  # Lower = higher priority
    
    # Adjustments
    distance_weight_factor = models.FloatField(default=1.0)  # How much distance affects weight
    time_decay_factor = models.FloatField(default=1.0)  # How much age affects weight
    
    # Flags
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)  # Primary source for this region
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Source Weight'
        verbose_name_plural = 'Source Weights'
        unique_together = [['source_code', 'region_code']]
        ordering = ['region_code', 'priority_rank']
        indexes = [
            models.Index(fields=['region_code', 'priority_rank']),
        ]

    def __str__(self):
        return f"{self.source_code} - {self.region_code} (Priority: {self.priority_rank})"


class FusionLog(TimeStampedModel):
    """
    Log of fusion operations for debugging and analysis.
    """
    # Query parameters
    query_lat = models.DecimalField(max_digits=9, decimal_places=6)
    query_lon = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Results
    result_aqi = models.IntegerField(null=True)
    sources_used = models.JSONField(default=list)
    sources_attempted = models.JSONField(default=list)
    sources_failed = models.JSONField(default=list)
    
    # Fusion details
    fusion_method = models.CharField(max_length=50)  # weighted_average, priority_select, etc.
    weight_details = models.JSONField(default=dict)
    
    # Performance
    execution_time_ms = models.IntegerField(null=True)
    cache_hit = models.BooleanField(default=False)
    
    # Errors
    has_error = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Fusion Log'
        verbose_name_plural = 'Fusion Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['has_error']),
        ]

    def __str__(self):
        return f"Fusion at ({self.query_lat}, {self.query_lon}) - {self.created_at}"
