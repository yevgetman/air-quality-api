"""
Base adapter class for all air quality data sources.
"""
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional

import requests
from django.conf import settings
from django.utils import timezone
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .models import SourceData, RawAPIResponse, AdapterStatus

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """
    Abstract base class for all data source adapters.
    Provides common functionality for API calls, caching, error handling, and data normalization.
    """
    
    # Subclasses must define these
    SOURCE_NAME = None
    SOURCE_CODE = None
    API_BASE_URL = None
    REQUIRES_API_KEY = True
    QUALITY_LEVEL = 'verified'
    
    def __init__(self):
        if not all([self.SOURCE_NAME, self.SOURCE_CODE, self.API_BASE_URL]):
            raise ValueError("Adapter must define SOURCE_NAME, SOURCE_CODE, and API_BASE_URL")
        
        self.settings = settings.AIR_QUALITY_SETTINGS
        self.api_key = self._get_api_key()
        self.session = self._create_session()
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from settings."""
        if not self.REQUIRES_API_KEY:
            return None
        
        api_key = settings.API_KEYS.get(self.SOURCE_CODE.replace('_', ''))
        if not api_key:
            logger.warning(f"No API key found for {self.SOURCE_NAME}")
        
        return api_key
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.settings.get('MAX_RETRIES', 3),
            backoff_factor=self.settings.get('RETRY_BACKOFF_FACTOR', 2),
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]  # Updated from method_whitelist
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Dict = None, 
        headers: Dict = None,
        method: str = 'GET'
    ) -> Optional[Dict]:
        """
        Make HTTP request with error handling and logging.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: HTTP headers
            method: HTTP method
            
        Returns:
            Response data as dict or None on error
        """
        url = f"{self.API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        params = params or {}
        headers = headers or {}
        
        start_time = time.time()
        
        try:
            # Add API key to request
            self._add_api_key(params, headers)
            
            # Make request
            timeout = self.settings.get('REQUEST_TIMEOUT', 10)
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log raw response
            self._log_response(
                endpoint=endpoint,
                params=params,
                response=response,
                response_time_ms=response_time_ms
            )
            
            # Check response
            response.raise_for_status()
            
            # Update adapter status
            self._update_status(success=True)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.SOURCE_NAME} API error: {e}")
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log error response
            self._log_response(
                endpoint=endpoint,
                params=params,
                response=getattr(e, 'response', None),
                response_time_ms=response_time_ms,
                error=str(e)
            )
            
            # Update adapter status
            self._update_status(success=False, error_message=str(e))
            
            return None
    
    def _add_api_key(self, params: Dict, headers: Dict):
        """
        Add API key to request. Override in subclass if needed.
        Default: adds to query params as 'api_key'.
        """
        if self.REQUIRES_API_KEY and self.api_key:
            params['api_key'] = self.api_key
    
    def _log_response(
        self, 
        endpoint: str, 
        params: Dict, 
        response: Optional[requests.Response],
        response_time_ms: int,
        error: str = None
    ):
        """Log API response to database."""
        try:
            status_code = response.status_code if response else 0
            is_error = bool(error) or (status_code >= 400)
            
            response_data = {}
            if response:
                try:
                    response_data = response.json()
                except Exception:
                    response_data = {'raw': response.text[:1000]}
            
            RawAPIResponse.objects.create(
                source=self.SOURCE_CODE,
                endpoint=endpoint,
                params=params,
                response_data=response_data,
                status_code=status_code,
                response_time_ms=response_time_ms,
                is_error=is_error,
                error_message=error or ''
            )
        except Exception as e:
            logger.error(f"Failed to log API response: {e}")
    
    def _update_status(self, success: bool, error_message: str = ''):
        """Update adapter status metrics."""
        try:
            status, created = AdapterStatus.objects.get_or_create(
                source=self.SOURCE_CODE,
                defaults={'is_active': True}
            )
            
            status.total_requests += 1
            
            if success:
                status.last_success_at = timezone.now()
                status.consecutive_failures = 0
            else:
                status.last_failure_at = timezone.now()
                status.consecutive_failures += 1
                status.total_failures += 1
                status.status_message = error_message
            
            # Auto-disable after too many failures
            if status.consecutive_failures >= 10:
                status.is_active = False
                logger.error(f"{self.SOURCE_NAME} auto-disabled after 10 consecutive failures")
            
            status.save()
            
        except Exception as e:
            logger.error(f"Failed to update adapter status: {e}")
    
    def normalize_data(self, raw_data: Dict, query_lat: float, query_lon: float) -> List[SourceData]:
        """
        Normalize raw API response to SourceData objects.
        Must be implemented by subclasses.
        
        Args:
            raw_data: Raw API response
            query_lat: Query latitude
            query_lon: Query longitude
            
        Returns:
            List of SourceData objects (not saved to DB)
        """
        raise NotImplementedError("Subclasses must implement normalize_data()")
    
    @abstractmethod
    def fetch_current(self, lat: float, lon: float, **kwargs) -> List[SourceData]:
        """
        Fetch current air quality data for coordinates.
        Must be implemented by subclasses.
        
        Args:
            lat: Latitude
            lon: Longitude
            **kwargs: Additional adapter-specific parameters
            
        Returns:
            List of SourceData objects
        """
        pass
    
    def fetch_forecast(self, lat: float, lon: float, **kwargs) -> List[Dict]:
        """
        Fetch forecast data (optional, override if supported).
        
        Args:
            lat: Latitude
            lon: Longitude
            **kwargs: Additional adapter-specific parameters
            
        Returns:
            List of forecast data dictionaries
        """
        return []
    
    def is_available(self) -> bool:
        """Check if adapter is available and healthy."""
        if not self.REQUIRES_API_KEY:
            return True
        
        if not self.api_key:
            return False
        
        try:
            status = AdapterStatus.objects.get(source=self.SOURCE_CODE)
            return status.is_healthy
        except AdapterStatus.DoesNotExist:
            return True
