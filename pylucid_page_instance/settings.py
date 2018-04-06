
"""
    page instance setting example
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Here should be only set stuff depend on page instance (e.g.: project path)
"""

from pathlib import Path

# PyLucid
from pylucid.base_settings import *


# For build paths inside the project:
BASE_DIR = Path(__file__).resolve().parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'Only for the tests ;)'


DEBUG = True

TEMPLATES[0]["DIRS"] = [str(Path(BASE_DIR, "templates/"))]
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# Don't cache template loading:
TEMPLATES[0]["OPTIONS"]['loaders']= [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]


STATIC_ROOT = str(Path(BASE_DIR, 'static'))
MEDIA_ROOT = str(Path(BASE_DIR, 'media'))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(Path(BASE_DIR, '..', 'test_project_db.sqlite3').resolve()),
    }
}

# Deactivate caches
# https://docs.djangoproject.com/en/1.11/topics/cache/#dummy-caching-for-development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# https://django-compressor.readthedocs.io/en/latest/settings/
# COMPRESS_ENABLED=False
COMPRESS_ENABLED=True


if DEBUG:
    # Turns on all warnings
    warnings.simplefilter("always")
