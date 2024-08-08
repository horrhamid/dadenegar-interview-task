from pathlib import Path
from getenv import env
import os

try:
    from .local_settings import *
except Exception as e:
    # not running on local
    pass


class ENV:
    API_VERSION = os.getenv("API_VERSION")
    API_LICENCE = os.getenv("API_LICENCE")

    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

    SUPERUSER_USERNAME = os.getenv("SUPERUSER_USERNAME")
    SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD")

    SWAGGER = os.getenv("SWAGGER") == "on"
    REDOC = os.getenv("REDOC") == "on"
    DJANGO_ADMIN = os.getenv("DJANGO_ADMIN") == "on"
    DEBUG = os.getenv("DEBUG") == "on"
    IS_LOCAL = os.getenv("LOCAL") == "on"
    REDIS_HOST = os.getenv("REDIS_HOST", default="localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", default="6379")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
    CELERY_RESULT_BACKEND = "django-db"


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ym%j)v=1k%k$7m8#f!wqj!7_*eu(w2*crv)&zo4z$g+i%e6_0j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
if not ENV.IS_LOCAL:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
AUTH_USER_MODEL = "authentication.User"
ROOT_URLCONF = "FormFlow.urls"
WSGI_APPLICATION = "FormFlow.wsgi.application"
APPEND_SLASH = True
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework_swagger",
    "django_celery_beat",
    "django_celery_results",
    "drf_yasg",
    "rest_framework",
    "authentication",
]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "authentication.middleware.TokenAuthentication",
    ],
}
MIDDLEWARE = [
    "authentication.middleware.TokenMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if ENV.SWAGGER:
    SWAGGER_SETTINGS = {
        "SECURITY_DEFINITIONS": {
            "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
        },
        "USE_SESSION_AUTH": False,
    }

ROOT_URLCONF = 'FormFlow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'FormFlow.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": ENV.POSTGRES_USER,
        "PASSWORD": ENV.POSTGRES_PASSWORD,
        "NAME": ENV.POSTGRES_DATABASE,
        "HOST": ENV.POSTGRES_HOST,
        "PORT": ENV.POSTGRES_PORT,
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
CELERY_RESULT_BACKEND = "django-db"
CELERY_TIMEZONE = "Asia/Tehran"
CELERY_TASK_TRACK_STARTED = True
CELERY_ACKS_LATE = True

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

REDIS_HOST = "localhost"
REDIS_PORT = "6379"



# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
