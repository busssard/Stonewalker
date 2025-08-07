import os
from urllib.parse import urlparse

DATABASES={
'default':urlparse(os.environ.get('DATABASE_URL')) # linked .env file to your settings

}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT=os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIR=[
    os.path.join(BASE_DIR, 'static')
]





IS_PRODUCTION = os.environ.get('IS_PRODUCTION')

if IS_PRODUCTION:
    from .conf.production.settings import *
else:
    from .conf.development.settings import *
