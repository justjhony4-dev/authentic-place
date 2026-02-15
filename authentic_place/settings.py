"""
Django settings for authentic_place project.
VERSION PRODUCTION OFFICIELLE - Render Ready
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# ======================================================
# BASE DIRECTORY
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ======================================================
# LOAD ENV VARIABLES
# ======================================================

load_dotenv(BASE_DIR / ".env")


# ======================================================
# SECURITY
# ======================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-change-this-immediately"
)

DEBUG = os.getenv("DEBUG", "False") == "True"


ALLOWED_HOSTS = [

    ".onrender.com",
    "localhost",
    "127.0.0.1",

]


# ======================================================
# APPLICATIONS
# ======================================================

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'widget_tweaks',

    'market',
    'pages',

]


# ======================================================
# MIDDLEWARE
# ======================================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]


# ======================================================
# URLS
# ======================================================

ROOT_URLCONF = 'authentic_place.urls'


# ======================================================
# TEMPLATES
# ======================================================

TEMPLATES = [

    {

        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / "templates",
        ],

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


# ======================================================
# WSGI
# ======================================================

WSGI_APPLICATION = 'authentic_place.wsgi.application'


# ======================================================
# DATABASE (POSTGRESQL RENDER READY)
# ======================================================


DATABASES = {

    'default': dj_database_url.config(

        default=os.getenv("DATABASE_URL"),

        conn_max_age=600,

        ssl_require=True

    )

}

# ======================================================
# PASSWORD VALIDATION
# ======================================================

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


# ======================================================
# INTERNATIONALIZATION
# ======================================================

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'America/Port-au-Prince'

USE_I18N = True

USE_TZ = True


# ======================================================
# STATIC FILES CONFIGURATION (CRITIQUE POUR RENDER)
# ======================================================

STATIC_URL = '/static/'


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


STATICFILES_DIRS = [

    BASE_DIR / "market/static",

]


STORAGES = {

    "default": {

        "BACKEND": "django.core.files.storage.FileSystemStorage",

    },

    "staticfiles": {

        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",

    },

}


# ======================================================
# MEDIA FILES
# ======================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ======================================================
# AUTH
# ======================================================

LOGIN_REDIRECT_URL = '/dashboard/'

LOGOUT_REDIRECT_URL = '/accounts/login/'

LOGIN_URL = '/accounts/login/'


# ======================================================
# DEFAULT PRIMARY KEY
# ======================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ======================================================
# RENDER SECURITY CONFIG
# ======================================================

if not DEBUG:

    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"

else:

    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = False

    CSRF_COOKIE_SECURE = False
