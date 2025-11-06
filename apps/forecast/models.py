"""
Models for air quality forecasts.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class ForecastData(TimeStampedModel):
    """
    Air quality forecast data from various sources.
    """
    # Location
    lat = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    
    # Forecast time (future timestamp)
    forecast_timestamp = models.DateTimeField(db_index=True)
    
    # Air quality prediction
    aqi = models.IntegerField()
    category = models.CharField(max_length=50, blank=True)
    
    # Pollutant predictions
    pollutants = models.JSONField(default=dict)
    
    # Source information
    source = models.CharField(max_length=50, db_index=True)
    
    # Metadata
    confidence_level = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ],
        default='medium'
    )
    
    # When this forecast was generated
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Forecast Data'
        verbose_name_plural = 'Forecast Data'
        ordering = ['forecast_timestamp']
        indexes = [
            models.Index(fields=['lat', 'lon', 'forecast_timestamp']),
            models.Index(fields=['source', 'forecast_timestamp']),
            models.Index(fields=['-generated_at']),
        ]

    def __str__(self):
        return f"Forecast AQI {self.aqi} at ({self.lat}, {self.lon}) for {self.forecast_timestamp}"


class AggregatedForecast(TimeStampedModel):
    """
    Aggregated forecast from multiple sources.
    """
    # Location
    lat = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    
    # Forecast time
    forecast_timestamp = models.DateTimeField(db_index=True)
    
    # Aggregated values
    aqi = models.IntegerField()
    category = models.CharField(max_length=50)
    pollutants = models.JSONField(default=dict)
    
    # Sources used
    sources = models.JSONField(default=list)
    source_count = models.IntegerField(default=0)
    
    # Cache
    cached_until = models.DateTimeField(db_index=True)

    class Meta:
        verbose_name = 'Aggregated Forecast'
        verbose_name_plural = 'Aggregated Forecasts'
        unique_together = [['lat', 'lon', 'forecast_timestamp']]
        ordering = ['forecast_timestamp']
        indexes = [
            models.Index(fields=['lat', 'lon', 'forecast_timestamp']),
            models.Index(fields=['cached_until']),
        ]

    def __str__(self):
        return f"Aggregated forecast AQI {self.aqi} for {self.forecast_timestamp}"
