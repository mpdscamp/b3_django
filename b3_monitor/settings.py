import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-REPLACE_WITH_RANDOM_SECRET'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local app
    'assets',
    
    # We do NOT need django-crontab anymore, replaced by Celery
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'b3_monitor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'b3_monitor/templates'],  # so we can place .html files in /templates/
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'b3_monitor.wsgi.application'

# Database: SQLite for MVP
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static Files
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'b3_monitor/static'
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration
# Make sure Redis is running on localhost:6379 or update as needed.
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Login/Logout Settings
LOGIN_REDIRECT_URL = 'asset_list'  # Redirect to assets page after login
LOGOUT_REDIRECT_URL = 'landing_page'  # Redirect to landing page after logout
LOGIN_URL = 'login'  # URL for the login page

# Email Settings for Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'b3stockmonitorinoachal@gmail.com'
EMAIL_HOST_PASSWORD = 'hfhn fyav tbag meko'

# Set both of these to ensure proper "From" address
DEFAULT_FROM_EMAIL = 'b3stockmonitorinoachal@gmail.com'
SERVER_EMAIL = 'b3stockmonitorinoachal@gmail.com'

# For development/testing, set this to True to see detailed email errors
EMAIL_DEBUG = True