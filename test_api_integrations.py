#!/usr/bin/env python
"""
API Integration Test Suite
Tests all external API integrations to verify keys are valid and endpoints return data.

Usage:
    python test_api_integrations.py
    
    Or from Django:
    python manage.py shell < test_api_integrations.py
"""

import os
import sys
import requests
from datetime import datetime
from typing import Dict, Optional, Tuple
from pprint import pprint

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")

def print_test(name: str, status: str, message: str = ""):
    """Print a test result."""
    if status == "PASS":
        symbol = "✓"
        color = Colors.GREEN
    elif status == "FAIL":
        symbol = "✗"
        color = Colors.RED
    elif status == "WARN":
        symbol = "⚠"
        color = Colors.YELLOW
    else:
        symbol = "◯"
        color = Colors.BLUE
    
    print(f"{color}{symbol} {name:<50}{Colors.END} {color}{status}{Colors.END}")
    if message:
        print(f"  {Colors.YELLOW}└─ {message}{Colors.END}")

def load_env_file():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print(f"{Colors.RED}Error: .env file not found{Colors.END}")
        return False
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    return True

def get_api_key(key_name: str) -> Optional[str]:
    """Get API key from environment."""
    key = os.environ.get(key_name)
    if not key or key == '':
        return None
    return key


class APITester:
    """Base class for API testing."""
    
    def __init__(self, name: str, api_key_env: str):
        self.name = name
        self.api_key = get_api_key(api_key_env)
        self.results = []
    
    def test(self) -> Tuple[bool, str]:
        """Override this method in subclasses."""
        raise NotImplementedError
    
    def run(self):
        """Run the test and print results."""
        print(f"\n{Colors.BOLD}Testing: {self.name}{Colors.END}")
        print("-" * 80)
        
        if not self.api_key:
            print_test("API Key Found", "FAIL", f"Key not found in environment")
            return False
        
        print_test("API Key Found", "PASS", f"Key: {self.api_key[:8]}...")
        
        try:
            success, message = self.test()
            if success:
                print_test("API Connection", "PASS", message)
                print_test("Data Retrieval", "PASS", "Valid data returned")
                return True
            else:
                print_test("API Connection", "FAIL", message)
                return False
        except Exception as e:
            print_test("API Connection", "FAIL", f"Exception: {str(e)}")
            return False


class AirNowTester(APITester):
    """Test EPA AirNow API."""
    
    def __init__(self):
        super().__init__("EPA AirNow", "AIRNOW_API_KEY")
    
    def test(self) -> Tuple[bool, str]:
        """Test AirNow observation endpoint."""
        # Los Angeles coordinates
        url = "https://www.airnowapi.org/aq/observation/latLong/current/"
        params = {
            'format': 'application/json',
            'latitude': 34.05,
            'longitude': -118.24,
            'distance': 25,
            'API_KEY': self.api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                # Check if we got valid data
                first_item = data[0]
                if 'AQI' in first_item and 'ParameterName' in first_item:
                    return True, f"Retrieved {len(data)} observation(s)"
            return False, "API returned empty or invalid data"
        elif response.status_code == 401:
            return False, "Invalid API key (401 Unauthorized)"
        elif response.status_code == 403:
            return False, "Access forbidden (403)"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"


class PurpleAirTester(APITester):
    """Test PurpleAir API."""
    
    def __init__(self):
        super().__init__("PurpleAir", "PURPLEAIR_API_KEY")
    
    def test(self) -> Tuple[bool, str]:
        """Test PurpleAir sensors endpoint."""
        # Los Angeles bounding box
        url = "https://api.purpleair.com/v1/sensors"
        headers = {
            'X-API-Key': self.api_key
        }
        params = {
            'fields': 'pm2.5,latitude,longitude,name',
            'nwlat': 34.10,
            'nwlng': -118.30,
            'selat': 34.00,
            'selng': -118.20,
            'max_age': 3600
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                return True, f"Retrieved {len(data['data'])} sensor(s)"
            return False, "API returned no sensors"
        elif response.status_code == 401:
            return False, "Invalid API key (401 Unauthorized)"
        elif response.status_code == 403:
            return False, "Access forbidden (403)"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"


class OpenWeatherMapTester(APITester):
    """Test OpenWeatherMap Air Pollution API."""
    
    def __init__(self):
        super().__init__("OpenWeatherMap", "OPENWEATHERMAP_API_KEY")
    
    def test(self) -> Tuple[bool, str]:
        """Test OpenWeatherMap air pollution endpoint."""
        url = "https://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            'lat': 34.05,
            'lon': -118.24,
            'appid': self.api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'list' in data and len(data['list']) > 0:
                item = data['list'][0]
                if 'main' in item and 'aqi' in item['main']:
                    aqi = item['main']['aqi']
                    return True, f"Retrieved AQI data (AQI: {aqi})"
            return False, "API returned invalid data structure"
        elif response.status_code == 401:
            return False, "Invalid API key (401 Unauthorized)"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"


class WAQITester(APITester):
    """Test WAQI (World Air Quality Index) API."""
    
    def __init__(self):
        super().__init__("WAQI (World Air Quality Index)", "WAQI_API_KEY")
    
    def test(self) -> Tuple[bool, str]:
        """Test WAQI geo feed endpoint."""
        url = "https://api.waqi.info/feed/geo:34.05;-118.24/"
        params = {
            'token': self.api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                if 'data' in data and 'aqi' in data['data']:
                    aqi = data['data']['aqi']
                    station = data['data'].get('city', {}).get('name', 'Unknown')
                    return True, f"Retrieved data from '{station}' (AQI: {aqi})"
                return False, "API returned invalid data structure"
            elif data.get('status') == 'error':
                return False, f"API error: {data.get('data', 'Unknown error')}"
            else:
                return False, "Unknown API response status"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"


class AirVisualTester(APITester):
    """Test AirVisual (IQAir) API."""
    
    def __init__(self):
        super().__init__("AirVisual (IQAir)", "AIRVISUAL_API_KEY")
    
    def test(self) -> Tuple[bool, str]:
        """Test AirVisual nearest city endpoint."""
        url = "https://api.airvisual.com/v2/nearest_city"
        params = {
            'lat': 34.05,
            'lon': -118.24,
            'key': self.api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                if 'data' in data and 'current' in data['data']:
                    city = data['data'].get('city', 'Unknown')
                    pollution = data['data']['current'].get('pollution', {})
                    aqius = pollution.get('aqius', 'N/A')
                    return True, f"Retrieved data for '{city}' (US AQI: {aqius})"
                return False, "API returned invalid data structure"
            elif data.get('status') == 'fail':
                return False, f"API error: {data.get('data', {}).get('message', 'Unknown error')}"
            else:
                return False, "Unknown API response status"
        elif response.status_code == 401:
            return False, "Invalid API key (401 Unauthorized)"
        elif response.status_code == 429:
            return False, "Rate limit exceeded (429)"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"


def test_forecast_endpoints():
    """Test forecast endpoints for supported APIs."""
    print_header("Testing Forecast Endpoints")
    
    # OpenWeatherMap Forecast
    owm_key = get_api_key('OPENWEATHERMAP_API_KEY')
    if owm_key:
        print(f"\n{Colors.BOLD}OpenWeatherMap Air Pollution Forecast:{Colors.END}")
        url = "https://api.openweathermap.org/data/2.5/air_pollution/forecast"
        params = {'lat': 34.05, 'lon': -118.24, 'appid': owm_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'list' in data:
                    print_test("Forecast Available", "PASS", f"{len(data['list'])} forecast hours")
                else:
                    print_test("Forecast Available", "FAIL", "No forecast data")
            else:
                print_test("Forecast Available", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            print_test("Forecast Available", "FAIL", f"Exception: {str(e)}")


def main():
    """Run all API integration tests."""
    print_header("Air Quality API Integration Tests")
    print(f"{Colors.BOLD}Test Date:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}Purpose:{Colors.END} Validate all external API keys and endpoints\n")
    
    # Load environment variables
    if not load_env_file():
        print(f"{Colors.RED}Please create a .env file with your API keys{Colors.END}")
        return 1
    
    print_test(".env File Loaded", "PASS", "Environment variables loaded")
    
    # Define all tests
    testers = [
        AirNowTester(),
        PurpleAirTester(),
        OpenWeatherMapTester(),
        WAQITester(),
        AirVisualTester(),
    ]
    
    # Run all tests
    results = []
    for tester in testers:
        result = tester.run()
        results.append((tester.name, result))
    
    # Test forecast endpoints
    test_forecast_endpoints()
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Results:{Colors.END}")
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {status} - {name}")
    
    print(f"\n{Colors.BOLD}Overall:{Colors.END} {passed}/{total} APIs working")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All API integrations are working!{Colors.END}\n")
        return 0
    else:
        failed = total - passed
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ {failed} API integration(s) failed{Colors.END}")
        print(f"{Colors.YELLOW}Please check the API keys and try again.{Colors.END}\n")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        sys.exit(130)
