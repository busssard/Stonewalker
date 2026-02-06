import os
import warnings
from pathlib import Path
from dotenv import load_dotenv  # type: ignore
from django.utils.translation import gettext_lazy as _
from os.path import dirname

warnings.simplefilter('error', DeprecationWarning)

BASE_DIR = dirname(dirname(dirname(dirname(os.path.abspath(__file__)))))
CONTENT_DIR = os.path.join(BASE_DIR, 'content')

# Load environment variables from .env files to avoid exporting each session
# Try project root and source/.env
_env_candidates = [
    Path(BASE_DIR) / '.env',
    Path(BASE_DIR) / 'source' / '.env',
]
for _env_path in _env_candidates:
    try:
        if _env_path.exists():
            load_dotenv(dotenv_path=_env_path, override=False)
    except Exception:
        # Loading .env is best-effort for local dev
        pass

SECRET_KEY = 'NhfTvayqggTBPswCXXhWaN69HuglgZIkM'

DEBUG = True
ALLOWED_HOSTS = []

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Vendor apps
    'bootstrap4',

    # Application apps
    'main',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(CONTENT_DIR, 'templates'),
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

WSGI_APPLICATION = 'app.wsgi.application'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(CONTENT_DIR, 'tmp/emails')
EMAIL_HOST_USER = 'test@example.com'
DEFAULT_FROM_EMAIL = 'test@example.com'

# Database: PostgreSQL required for development
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it to your PostgreSQL connection string. "
        "Example: postgresql://user:password@localhost:5432/dbname"
    )

# Parse DATABASE_URL for PostgreSQL
# Skip dj_database_url due to Python 3.8 compatibility issues
# Use manual parsing instead
if DATABASE_URL.startswith(('postgresql://', 'postgres://')):
    import urllib.parse
    parsed = urllib.parse.urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path[1:],  # Remove leading /
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or 5432,
            'OPTIONS': {
                'sslmode': 'prefer',  # Use SSL if available, but don't require it for local dev
            }
        }
    }
else:
    raise ValueError(f"Invalid DATABASE_URL format: {DATABASE_URL}. Must be postgresql://... or postgres://...")

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

ENABLE_USER_ACTIVATION = True
DISABLE_USERNAME = False
LOGIN_VIA_EMAIL = True
LOGIN_VIA_EMAIL_OR_USERNAME = False
LOGIN_REDIRECT_URL = 'index'
LOGIN_URL = 'accounts:log_in'
USE_REMEMBER_ME = True

RESTORE_PASSWORD_VIA_EMAIL_OR_USERNAME = False
ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE = True

SIGN_UP_FIELDS = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
if DISABLE_USERNAME:
    SIGN_UP_FIELDS = ['first_name', 'last_name', 'email', 'password1', 'password2']

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

USE_I18N = True
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _('English')),
    ('ru', _('Russian')),
    ('zh-hans', _('Simplified Chinese')),
    ('fr', _('French')),
    ('es', _('Spanish')),
    ('de', _('German')),
    ('it', _('Italian')),
]

# Language detection settings
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = None  # Session cookie
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_SECURE = False
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = 'Lax'

TIME_ZONE = 'UTC'
USE_TZ = True

STATIC_ROOT = os.path.join(CONTENT_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(CONTENT_DIR, 'media')
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(CONTENT_DIR, 'assets'),
]

LOCALE_PATHS = [
    os.path.join(CONTENT_DIR, 'locale')
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Stripe Configuration
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

# Shop Configuration
SHOP_CONFIG_PATH = os.path.join(BASE_DIR, 'main', 'shop_config.json')

# Discourse SSO Configuration
DISCOURSE_URL = os.environ.get('DISCOURSE_URL', 'http://localhost:4200')
DISCOURSE_SSO_SECRET = os.environ.get('DISCOURSE_SSO_SECRET', 'dev_secret_change_me')
DISCOURSE_SSO_ENABLED = True
