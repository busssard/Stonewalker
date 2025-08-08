import os

# Determine environment from boolean-like env var
IS_PRODUCTION = os.environ.get('IS_PRODUCTION', '').strip().lower() in ('1', 'true', 'yes', 'on')

if IS_PRODUCTION:
    from .conf.production.settings import *  # noqa: F401,F403
else:
    from .conf.development.settings import *  # noqa: F401,F403
