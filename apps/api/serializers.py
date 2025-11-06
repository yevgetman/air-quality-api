"""
DRF serializers for API responses.
"""
from rest_framework import serializers


class PollutantSerializer(serializers.Serializer):
    """Serializer for pollutant concentrations."""
    pm25 = serializers.FloatField(required=False, allow_null=True)
    pm10 = serializers.FloatField(required=False, allow_null=True)
    o3 = serializers.FloatField(required=False, allow_null=True)
    no2 = serializers.FloatField(required=False, allow_null=True)
    so2 = serializers.FloatField(required=False, allow_null=True)
    co = serializers.FloatField(required=False, allow_null=True)


class CurrentAirQualitySerializer(serializers.Serializer):
    """Serializer for current air quality data."""
    aqi = serializers.IntegerField(allow_null=True)
    category = serializers.CharField()
    pollutants = PollutantSerializer()
    sources = serializers.ListField(child=serializers.CharField())
    last_updated = serializers.DateTimeField()


class LocationSerializer(serializers.Serializer):
    """Serializer for location information."""
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    city = serializers.CharField(allow_blank=True, required=False)
    region = serializers.CharField(allow_blank=True, required=False)
    country = serializers.CharField(allow_blank=True, required=False)


class ForecastItemSerializer(serializers.Serializer):
    """Serializer for a single forecast item."""
    timestamp = serializers.DateTimeField()
    aqi = serializers.IntegerField()
    category = serializers.CharField()
    pollutants = PollutantSerializer(required=False)
    sources = serializers.ListField(child=serializers.CharField(), required=False)


class AirQualityResponseSerializer(serializers.Serializer):
    """Main response serializer for air quality endpoint."""
    location = LocationSerializer()
    current = CurrentAirQualitySerializer()
    forecast = ForecastItemSerializer(many=True, required=False)
    health_advice = serializers.CharField(required=False)
    source_details = serializers.ListField(required=False)


class ErrorSerializer(serializers.Serializer):
    """Serializer for error responses."""
    error = serializers.CharField()
    detail = serializers.CharField(required=False)
    code = serializers.CharField(required=False)
