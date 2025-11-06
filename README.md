# Air Quality API - Django Microservice

A comprehensive Django-based microservice that blends multiple air quality data sources to provide unified, hyper-local, real-time air quality information for U.S. and Canadian locations.

## 📘 For API Users

**Want to integrate this API into your application?** 

👉 **See [README-API-REFERENCE.md](README-API-REFERENCE.md)** for complete API documentation with examples, use cases, and integration guides.

---

## 🌟 Features

- **Multi-Source Data Fusion**: Blends data from EPA AirNow, PurpleAir, OpenWeatherMap, WAQI, and AirVisual
- **Intelligent Weighting**: Prioritizes data based on source trust, freshness, distance, and quality
- **Hyper-Local Data**: Utilizes community sensors for precise local measurements
- **Forecast Support**: Aggregates 4-day air quality forecasts
- **Region-Specific**: Optimized source priorities for U.S. and Canada
- **Caching Layer**: Redis-backed caching for performance
- **RESTful API**: Clean, well-documented endpoints
- **Admin Interface**: Django admin for monitoring and configuration

## 📋 Architecture

The system follows a layered microservice architecture:

1. **API Gateway** - REST endpoints with validation and rate limiting
2. **Location Resolution** - Geocoding and region detection with caching
3. **Data Adapters** - Modular adapters for each data source
4. **Fusion Engine** - Intelligent blending with weighted averaging
5. **Forecast Aggregator** - Multi-source forecast merging
6. **Response Generator** - Unified response formatting

See [air_api_architecture.md](air_api_architecture.md) for detailed architecture documentation.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+ (or SQLite for development)
- Redis 6+ (optional, for caching)
- API Keys for data sources

### Installation

1. **Clone the repository**
```bash
cd /Users/yev/Sites/air-api
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements/development.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and database settings
```

5. **Create database**
```bash
# For PostgreSQL
createdb airquality_db

# For SQLite (default), skip this step
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Initialize default data**
```bash
python manage.py init_data
```

8. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

9. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

## 📡 API Endpoints

### Get Air Quality Data

```http
GET /api/v1/air-quality/?lat=34.05&lon=-118.24
```

**Parameters:**
- `lat` (required): Latitude
- `lon` (required): Longitude
- `include_forecast` (optional): Include forecast data (true/false)
- `radius_km` (optional): Search radius for sensors (default: 25, max: 100)
- `no_cache` (optional): Skip cache (true/false)

**Response:**
```json
{
  "location": {
    "lat": 34.05,
    "lon": -118.24,
    "city": "Los Angeles",
    "region": "CA",
    "country": "US"
  },
  "current": {
    "aqi": 72,
    "category": "Moderate",
    "pollutants": {
      "pm25": 13.2,
      "pm10": 19.7,
      "o3": 31.2,
      "no2": 10.4
    },
    "sources": ["EPA_AIRNOW", "PURPLEAIR"],
    "last_updated": "2025-11-05T12:03:00Z"
  },
  "health_advice": "Air quality is acceptable...",
  "forecast": [...]
}
```

### Get Health Advice

```http
GET /api/v1/health-advice/?aqi=72&scale=EPA
```

### List Data Sources

```http
GET /api/v1/sources/
```

### Health Check

```http
GET /api/v1/health/
```

## 🔑 API Keys

The application requires API keys for the following services:

1. **EPA AirNow** - Free, register at [airnowapi.org](https://docs.airnowapi.org/)
2. **PurpleAir** - Free tier available at [purpleair.com](https://www2.purpleair.com/pages/api)
3. **OpenWeatherMap** - Free tier at [openweathermap.org](https://openweathermap.org/api)
4. **WAQI** - Free for non-commercial at [aqicn.org/api](https://aqicn.org/api/)
5. **AirVisual** - Free tier available at [iqair.com/air-pollution-data-api](https://www.iqair.com/air-pollution-data-api)

Add your keys to the `.env` file:

```env
AIRNOW_API_KEY=your_key_here
PURPLEAIR_API_KEY=your_key_here
OPENWEATHERMAP_API_KEY=your_key_here
WAQI_API_KEY=your_key_here
AIRVISUAL_API_KEY=your_key_here
```

## 🏗️ Project Structure

```
air-api/
├── config/                      # Django settings
│   ├── settings/
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Dev settings
│   │   └── production.py       # Prod settings
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                   # Core models and utilities
│   ├── location/               # Location resolution
│   ├── adapters/               # Data source adapters
│   ├── fusion/                 # Data blending engine
│   ├── forecast/               # Forecast aggregation
│   └── api/                    # API endpoints
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── manage.py
└── README.md
```

## 🔧 Configuration

### Database

**PostgreSQL (recommended for production):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/airquality_db
```

**SQLite (development):**
```env
DATABASE_URL=sqlite:///db.sqlite3
```

### Redis Cache

```env
REDIS_URL=redis://localhost:6379/0
```

### Source Weights

Customize source weights and priorities in Django admin or via `SourceWeight` model:

```python
SourceWeight.objects.create(
    source_code='EPA_AIRNOW',
    region_code='US',
    priority_rank=1,
    trust_weight=1.0,
    is_primary=True
)
```

## 🧪 Testing

### Test API Integrations
Verify all external API keys are valid and endpoints are accessible:

```bash
# Quick test all API integrations
python test_api_integrations.py

# Expected output: ✓ All API integrations are working!
```

See [`API_INTEGRATION_TESTING.md`](API_INTEGRATION_TESTING.md) for detailed testing documentation.

### Unit and Integration Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific test file
pytest apps/adapters/tests/test_airnow.py
```

## 📊 Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to:

- View and manage data sources
- Monitor adapter health and API response logs
- Configure source weights and priorities
- View cached data and fusion logs
- Manage AQI categories and region configs

## 🚢 Deployment

### Production Checklist

1. ✅ Set `DEBUG=False` in production settings
2. ✅ Configure `SECRET_KEY` with strong random value
3. ✅ Set up PostgreSQL database
4. ✅ Configure Redis for caching
5. ✅ Set `ALLOWED_HOSTS` to your domain
6. ✅ Configure SSL/HTTPS
7. ✅ Set up Sentry for error tracking (optional)
8. ✅ Use Gunicorn or uWSGI as WSGI server
9. ✅ Configure nginx as reverse proxy
10. ✅ Set up monitoring and logging

### Docker Deployment (Optional)

```dockerfile
# Example Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements/production.txt .
RUN pip install -r production.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Environment Variables for Production

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SENTRY_DSN=https://...
```

## 📝 Data Sources Documentation

Detailed information about each data source is available in [air_quality_api_sources.md](air_quality_api_sources.md):

- **EPA AirNow**: Official U.S. AQI data
- **PurpleAir**: Community PM2.5 sensors
- **OpenWeatherMap**: Global atmospheric models
- **WAQI**: Worldwide data aggregator
- **AirVisual (IQAir)**: Global air quality data and city rankings
- **ECCC AQHI**: Canadian official data

## 🔄 Data Fusion Logic

The fusion engine uses weighted averaging with multiple factors:

1. **Source Trust Weight**: Base reliability (1.0 for official, 0.85 for sensors, 0.7 for models)
2. **Time Decay**: Recent data weighted higher (exponential decay)
3. **Distance Weight**: Closer sensors weighted higher
4. **Quality Level**: Verified > Sensor > Model > Estimated
5. **Confidence Score**: Sensor-specific confidence metrics

Final weight = Trust × Time × Distance × Quality × Confidence

## 📈 Performance

- **Response Time**: < 2 seconds typical (with cache: < 100ms)
- **Cache Hit Rate**: > 80% (10-minute TTL)
- **Throughput**: 100+ requests/minute per instance
- **Availability**: 99.5%+ with proper monitoring

## 🐛 Troubleshooting

### Common Issues

**1. API returns no data:**
- Check API keys in `.env` file
- Verify adapter health: `GET /api/v1/sources/`
- Check logs: `tail -f logs/airquality.log`

**2. Cache not working:**
- Ensure Redis is running: `redis-cli ping`
- Check `REDIS_URL` in `.env`

**3. Database errors:**
- Run migrations: `python manage.py migrate`
- Check database connection in `.env`

**4. Import errors:**
- Verify virtual environment is activated
- Reinstall requirements: `pip install -r requirements/development.txt`

## 📚 Additional Documentation

- [Architecture Overview](air_api_architecture.md)
- [API Sources Documentation](air_quality_api_sources.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- API Documentation (Swagger): `/api/v1/docs/` (when enabled)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run tests and linting
5. Submit a pull request

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- EPA AirNow for official U.S. air quality data
- PurpleAir for community sensor network
- OpenWeatherMap for global atmospheric data
- WAQI for worldwide data aggregation
- AirVisual (IQAir) for global air quality coverage

## 📞 Support

For issues or questions:
- Open a GitHub issue
- Check existing documentation
- Review logs and error messages

---

**Built with Django • Powered by Multiple Data Sources • Optimized for Accuracy**
