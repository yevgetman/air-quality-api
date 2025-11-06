"""
Management command to initialize database with default data.
"""
from django.core.management.base import BaseCommand
from apps.core.models import AQICategory, DataSource
from apps.core.constants import EPA_AQI_CATEGORIES, AQHI_CATEGORIES, DATA_SOURCES
from apps.location.models import RegionConfig
from apps.fusion.models import SourceWeight


class Command(BaseCommand):
    help = 'Initialize database with AQI categories, data sources, and default configurations'

    def handle(self, *args, **options):
        self.stdout.write('Initializing database with default data...\n')
        
        # Initialize AQI Categories
        self.init_aqi_categories()
        
        # Initialize Data Sources
        self.init_data_sources()
        
        # Initialize Region Configs
        self.init_region_configs()
        
        # Initialize Source Weights
        self.init_source_weights()
        
        self.stdout.write(self.style.SUCCESS('\nDatabase initialization complete!'))

    def init_aqi_categories(self):
        """Initialize AQI categories for EPA and AQHI scales."""
        self.stdout.write('Creating AQI categories...')
        
        count = 0
        
        # EPA categories
        for category_data in EPA_AQI_CATEGORIES:
            _, created = AQICategory.objects.get_or_create(
                scale=category_data['scale'],
                min_value=category_data['min_value'],
                max_value=category_data['max_value'],
                defaults={
                    'category': category_data['category'],
                    'color_hex': category_data['color_hex'],
                    'health_message': category_data['health_message'],
                    'sensitive_groups': category_data['sensitive_groups'],
                }
            )
            if created:
                count += 1
        
        # AQHI categories
        for category_data in AQHI_CATEGORIES:
            _, created = AQICategory.objects.get_or_create(
                scale=category_data['scale'],
                min_value=category_data['min_value'],
                max_value=category_data['max_value'],
                defaults={
                    'category': category_data['category'],
                    'color_hex': category_data['color_hex'],
                    'health_message': category_data['health_message'],
                    'sensitive_groups': category_data['sensitive_groups'],
                }
            )
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {count} AQI categories'))

    def init_data_sources(self):
        """Initialize data source registry."""
        self.stdout.write('Creating data sources...')
        
        sources_config = {
            'EPA_AIRNOW': {
                'name': 'EPA AirNow',
                'source_type': 'OFFICIAL',
                'description': 'Official U.S. EPA air quality data',
                'api_endpoint': 'https://www.airnowapi.org/aq/',
                'countries_covered': ['US'],
                'rate_limit_per_minute': 60,
                'default_trust_weight': 1.0,
            },
            'PURPLEAIR': {
                'name': 'PurpleAir',
                'source_type': 'SENSOR',
                'description': 'Community air quality sensors',
                'api_endpoint': 'https://api.purpleair.com/v1/',
                'countries_covered': [],  # Global
                'rate_limit_per_minute': 30,
                'default_trust_weight': 0.85,
            },
            'OPENWEATHERMAP': {
                'name': 'OpenWeatherMap',
                'source_type': 'MODEL',
                'description': 'Global atmospheric model',
                'api_endpoint': 'https://api.openweathermap.org/data/2.5/',
                'countries_covered': [],  # Global
                'rate_limit_per_minute': 60,
                'default_trust_weight': 0.7,
            },
            'WAQI': {
                'name': 'World Air Quality Index',
                'source_type': 'AGGREGATOR',
                'description': 'Global air quality data aggregator',
                'api_endpoint': 'https://api.waqi.info/',
                'countries_covered': [],  # Global
                'rate_limit_per_minute': 100,
                'default_trust_weight': 0.65,
            },
            'ECCC_AQHI': {
                'name': 'ECCC AQHI',
                'source_type': 'OFFICIAL',
                'description': 'Environment and Climate Change Canada',
                'api_endpoint': 'https://api.weather.gc.ca/collections/',
                'countries_covered': ['CA'],
                'rate_limit_per_minute': 60,
                'default_trust_weight': 1.0,
            },
            'AIRVISUAL': {
                'name': 'AirVisual (IQAir)',
                'source_type': 'MODEL',
                'description': 'Global air quality data from IQAir',
                'api_endpoint': 'https://api.airvisual.com/v2/',
                'countries_covered': [],  # Global
                'rate_limit_per_minute': 10,
                'default_trust_weight': 0.75,
            },
        }
        
        count = 0
        for code, config in sources_config.items():
            _, created = DataSource.objects.get_or_create(
                code=code,
                defaults=config
            )
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {count} data sources'))

    def init_region_configs(self):
        """Initialize region-specific configurations."""
        self.stdout.write('Creating region configurations...')
        
        regions = [
            {
                'country_code': 'US',
                'country_name': 'United States',
                'source_priority': ['EPA_AIRNOW', 'PURPLEAIR', 'OPENWEATHERMAP', 'WAQI'],
                'default_aqi_scale': 'EPA',
                'has_official_data': True,
            },
            {
                'country_code': 'CA',
                'country_name': 'Canada',
                'source_priority': ['ECCC_AQHI', 'PURPLEAIR', 'OPENWEATHERMAP', 'WAQI'],
                'default_aqi_scale': 'AQHI',
                'has_official_data': True,
            },
        ]
        
        count = 0
        for region_data in regions:
            _, created = RegionConfig.objects.get_or_create(
                country_code=region_data['country_code'],
                defaults=region_data
            )
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {count} region configurations'))

    def init_source_weights(self):
        """Initialize source weight configurations."""
        self.stdout.write('Creating source weights...')
        
        # US weights
        us_weights = [
            ('EPA_AIRNOW', 1, 1.0, True),
            ('PURPLEAIR', 2, 0.85, False),
            ('OPENWEATHERMAP', 3, 0.7, False),
            ('AIRVISUAL', 4, 0.75, False),
            ('WAQI', 5, 0.65, False),
        ]
        
        # Canada weights
        ca_weights = [
            ('ECCC_AQHI', 1, 1.0, True),
            ('PURPLEAIR', 2, 0.85, False),
            ('OPENWEATHERMAP', 3, 0.7, False),
            ('AIRVISUAL', 4, 0.75, False),
            ('WAQI', 5, 0.65, False),
        ]
        
        # Default weights
        default_weights = [
            ('OPENWEATHERMAP', 1, 0.7, True),
            ('AIRVISUAL', 2, 0.75, False),
            ('WAQI', 3, 0.65, False),
            ('PURPLEAIR', 4, 0.85, False),
        ]
        
        count = 0
        
        for source_code, priority, trust, is_primary in us_weights:
            _, created = SourceWeight.objects.get_or_create(
                source_code=source_code,
                region_code='US',
                defaults={
                    'priority_rank': priority,
                    'trust_weight': trust,
                    'is_primary': is_primary,
                }
            )
            if created:
                count += 1
        
        for source_code, priority, trust, is_primary in ca_weights:
            _, created = SourceWeight.objects.get_or_create(
                source_code=source_code,
                region_code='CA',
                defaults={
                    'priority_rank': priority,
                    'trust_weight': trust,
                    'is_primary': is_primary,
                }
            )
            if created:
                count += 1
        
        for source_code, priority, trust, is_primary in default_weights:
            _, created = SourceWeight.objects.get_or_create(
                source_code=source_code,
                region_code='DEFAULT',
                defaults={
                    'priority_rank': priority,
                    'trust_weight': trust,
                    'is_primary': is_primary,
                }
            )
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {count} source weights'))
