"""
WAQI (World Air Quality Index) adapter for global air quality data.
"""
import logging
from datetime import datetime
from typing import List, Dict

from django.utils import timezone
from apps.core.utils import calculate_distance_km

from .base import BaseAdapter
from .models import SourceData

logger = logging.getLogger(__name__)


class WAQIAdapter(BaseAdapter):
    """
    Adapter for WAQI API (aqicn.org).
    Global air quality data aggregated from various sources.
    """
    
    SOURCE_NAME = "WAQI"
    SOURCE_CODE = "WAQI"
    API_BASE_URL = "https://api.waqi.info/"
    REQUIRES_API_KEY = True
    QUALITY_LEVEL = "verified"
    
    def _add_api_key(self, params: Dict, headers: Dict):
        """WAQI uses 'token' parameter."""
        if self.api_key:
            params['token'] = self.api_key
    
    def fetch_current(self, lat: float, lon: float, **kwargs) -> List[SourceData]:
        """
        Fetch current air quality data for nearest station.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            List of SourceData objects
        """
        endpoint = f"feed/geo:{lat};{lon}/"
        
        raw_data = self._make_request(endpoint)
        
        if not raw_data or raw_data.get('status') != 'ok':
            return []
        
        return self.normalize_data(raw_data, lat, lon)
    
    def fetch_nearby_stations(self, lat: float, lon: float, radius_km: float = 25) -> List[SourceData]:
        """
        Fetch data from multiple nearby stations within bounding box.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers
            
        Returns:
            List of SourceData objects
        """
        # Calculate bounding box
        # Approximate: 1 degree ≈ 111 km
        degree_offset = radius_km / 111.0
        
        latlng = f"{lat-degree_offset},{lon-degree_offset},{lat+degree_offset},{lon+degree_offset}"
        endpoint = f"map/bounds/?latlng={latlng}"
        
        raw_data = self._make_request(endpoint)
        
        if not raw_data or raw_data.get('status') != 'ok':
            return []
        
        return self._normalize_map_data(raw_data, lat, lon)
    
    def normalize_data(self, raw_data: Dict, query_lat: float, query_lon: float) -> List[SourceData]:
        """
        Normalize WAQI response to SourceData objects.
        """
        if 'data' not in raw_data:
            return []
        
        data = raw_data['data']
        
        try:
            # Get station info
            station_name = data.get('city', {}).get('name', 'Unknown')
            station_location = data.get('city', {}).get('geo', [])
            
            if len(station_location) == 2:
                station_lat = station_location[0]
                station_lon = station_location[1]
                distance = calculate_distance_km(
                    query_lat, query_lon,
                    float(station_lat), float(station_lon)
                )
            else:
                station_lat = query_lat
                station_lon = query_lon
                distance = 0.0
            
            # Get AQI
            aqi = data.get('aqi')
            if isinstance(aqi, str) and aqi == '-':
                aqi = None
            else:
                try:
                    aqi = int(aqi)
                except (ValueError, TypeError):
                    aqi = None
            
            # Get timestamp
            time_data = data.get('time', {})
            timestamp_iso = time_data.get('iso')
            if timestamp_iso:
                try:
                    timestamp = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
                    if not timezone.is_aware(timestamp):
                        timestamp = timezone.make_aware(timestamp)
                except Exception:
                    timestamp = timezone.now()
            else:
                timestamp = timezone.now()
            
            # Extract pollutants
            iaqi = data.get('iaqi', {})
            pollutants = {}
            
            pollutant_map = {
                'pm25': 'pm25',
                'pm10': 'pm10',
                'o3': 'o3',
                'no2': 'no2',
                'so2': 'so2',
                'co': 'co',
            }
            
            for waqi_key, our_key in pollutant_map.items():
                if waqi_key in iaqi and 'v' in iaqi[waqi_key]:
                    pollutants[our_key] = iaqi[waqi_key]['v']
            
            source_data = SourceData(
                source=self.SOURCE_CODE,
                lat=station_lat,
                lon=station_lon,
                timestamp=timestamp,
                aqi=aqi,
                pollutants=pollutants,
                quality_level=self.QUALITY_LEVEL,
                distance_km=round(distance, 2),
                confidence_score=85.0,
                station_id=str(data.get('idx', '')),
                station_name=station_name,
            )
            
            return [source_data]
            
        except Exception as e:
            logger.error(f"Error parsing WAQI data: {e}")
            return []
    
    def _normalize_map_data(self, raw_data: Dict, query_lat: float, query_lon: float) -> List[SourceData]:
        """
        Normalize WAQI map/bounds response with multiple stations.
        """
        if 'data' not in raw_data:
            return []
        
        stations = raw_data['data']
        source_data_list = []
        
        for station in stations:
            try:
                # Get station info
                station_lat = station.get('lat')
                station_lon = station.get('lon')
                
                if not station_lat or not station_lon:
                    continue
                
                distance = calculate_distance_km(
                    query_lat, query_lon,
                    float(station_lat), float(station_lon)
                )
                
                # Get AQI
                aqi = station.get('aqi')
                if isinstance(aqi, str) and aqi == '-':
                    continue
                
                try:
                    aqi = int(aqi)
                except (ValueError, TypeError):
                    continue
                
                source_data = SourceData(
                    source=self.SOURCE_CODE,
                    lat=station_lat,
                    lon=station_lon,
                    timestamp=timezone.now(),  # Map data doesn't include timestamps
                    aqi=aqi,
                    pollutants={},  # Map data doesn't include detailed pollutants
                    quality_level=self.QUALITY_LEVEL,
                    distance_km=round(distance, 2),
                    confidence_score=80.0,
                    station_id=str(station.get('uid', '')),
                    station_name=station.get('station', {}).get('name', 'Unknown'),
                )
                
                source_data_list.append((distance, source_data))
                
            except Exception as e:
                logger.error(f"Error parsing WAQI station: {e}")
                continue
        
        # Sort by distance
        source_data_list.sort(key=lambda x: x[0])
        return [sd for _, sd in source_data_list]
