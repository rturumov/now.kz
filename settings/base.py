"""
Django settings for now_kz project.
"""

# Python modules
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

NOWKZ_ENV_ID = os.getenv("NOWKZ_ENV_ID", "local")
print(f"Current environment: {NOWKZ_ENV_ID}")

# ----------------------------------------------
# Path
#
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = "settings.urls"
WSGI_APPLICATION = "settings.wsgi.application"
ASGI_APPLICATION = "settings.asgi.application"

# ----------------------------------------------
# Security
#
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-key",
)

DEBUG = True
ALLOWED_HOSTS: list[str] = []

# ----------------------------------------------
# Applications
#
DJANGO_AND_THIRD_PARTY_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # DRF & libs
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "drf_spectacular",
]

PROJECT_APPS = [
    "apps.news.apps.NewsConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.comments.apps.CommentsConfig",
    "apps.abstracts.apps.AbstractsConfig",
]

INSTALLED_APPS = DJANGO_AND_THIRD_PARTY_APPS + PROJECT_APPS

AUTH_USER_MODEL = "accounts.User"

# ----------------------------------------------
# Middleware | Templates | Validators
#
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------------------------
# Database
#
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ----------------------------------------------
# DRF
#
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "now.kz API",
    "DESCRIPTION": "API documentation for now.kz news platform",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# ----------------------------------------------
# Internationalization
#
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ----------------------------------------------
# Static | Media
#
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"