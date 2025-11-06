"""
Development settings for Air Quality API project.
"""
from .base import *

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Additional apps for development
INSTALLED_APPS += [
    'debug_toolbar',
]

# Remove django_ratelimit in development since it requires Redis
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_ratelimit']

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Use console backend for emails in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching in development (Redis not required)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable rate limiting in development
REST_FRAMEWORK = REST_FRAMEWORK.copy()
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

# More verbose logging in development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework - Add browsable API in development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]
