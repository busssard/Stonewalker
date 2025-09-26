import os
from os.path import dirname
from django.utils.translation import gettext_lazy as _

BASE_DIR = dirname(dirname(dirname(dirname(os.path.abspath(__file__)))))
CONTENT_DIR = os.path.join(BASE_DIR, 'content')

SECRET_KEY = os.environ.get('SECRET_KEY', '3d305kajG5Jy8KBafCMpHwDIsNi0SqVaW')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'example.com,.netlify.app,.netlify.com,.onrender.com,localhost,127.0.0.1').split(',')

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    

    # Vendor apps
    'bootstrap4',

    # Application apps
    'main',
    'accounts',
]
DEFAULT_FROM_EMAIL = ['mail@stonewalker.org']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = os.environ.get('SENDGRID_EMAIL_USERNAME')
DEFAULT_FROM_EMAIL = 'noreply@stonewalker.org'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_EMAIL_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


# Database: PostgreSQL required for production
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required for production. "
        "Please set it to your PostgreSQL connection string. "
        "Example: postgresql://user:password@host:port/dbname"
    )

# Parse DATABASE_URL for PostgreSQL
try:
    import dj_database_url  # type: ignore
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True,
        )
    }
except Exception:
    # Fallback: manual PostgreSQL parsing (dj_database_url has compatibility issues with Python 3.8)
    if DATABASE_URL.startswith('postgresql://'):
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
                'CONN_MAX_AGE': 600,
                'OPTIONS': {
                    'sslmode': 'require',
                }
            }
        }
    else:
        raise ValueError(f"Invalid DATABASE_URL format: {DATABASE_URL}. Must be postgresql://...")

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
LOGIN_VIA_EMAIL = False
LOGIN_VIA_EMAIL_OR_USERNAME = True
LOGIN_REDIRECT_URL = 'index'
LOGIN_URL = 'accounts:log_in'
USE_REMEMBER_ME = False

RESTORE_PASSWORD_VIA_EMAIL_OR_USERNAME = True
EMAIL_ACTIVATION_AFTER_CHANGING = True

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

# Enable WhiteNoise for static files on Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = os.path.join(CONTENT_DIR, 'media')
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(CONTENT_DIR, 'assets'),
]

LOCALE_PATHS = [
    os.path.join(CONTENT_DIR, 'locale')
]

SIGN_UP_FIELDS = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
if DISABLE_USERNAME:
    SIGN_UP_FIELDS = ['first_name', 'last_name', 'email', 'password1', 'password2']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Log Django request errors to console (visible in Render logs)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
