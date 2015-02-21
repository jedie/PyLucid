# coding: utf-8

"""
    Django settings for example_project project
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Quick-start development settings - unsuitable for production:
        https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

    For more information on this file, see:
        https://docs.djangoproject.com/en/1.7/topics/settings/

    For the full list of settings and their values, see:
        https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Load the PyLucid base settings
from pylucid.base_settings import *


BASE_DIR = "/path/to/page_instance/"
DATA_DIR = os.path.abspath(os.path.dirname(__file__))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "CHANGE ME!!!"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True


MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
STATIC_ROOT = os.path.join(DATA_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'example_project', 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'example_project', 'templates'),
)


ROOT_URLCONF = 'example_project.urls'

WSGI_APPLICATION = 'example_project.wsgi.application'


INSTALLED_APPS += (
    'example_project',

    # Activate for PyLucid v1.x migration (must be added before 'pylucid' ;)
    # "pylucid_migration",

    # Activate for debugging:
    # 'debug_toolbar', # https://github.com/django-debug-toolbar/django-debug-toolbar
    # 'pylucid_debug', # Must be the last App!
)


INTERNAL_IPS = (
    '127.0.0.1',
    '::1',
)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'NAME': os.path.join(BASE_DIR, 'example_project.db'),
        'PASSWORD': '',
        'HOST': 'localhost',
        'USER': '',
        'ENGINE': 'django.db.backends.sqlite3',
        'PORT': ''
    }
    # Activate for PyLucid v1.x migration:
    # 'legacy': {
    #     'NAME': 'PyLucid_v1_Database',
    #     'PASSWORD': '',
    #     'HOST': 'localhost',
    #     'USER': '',
    #     # 'ENGINE': 'django.db.backends.mysql',
    #     'ENGINE': 'mysql_cymysql', # https://pypi.python.org/pypi/django-cymysql/
    #     'PORT': ''
    # }
}
# Activate for PyLucid v1.x migration
#DATABASE_ROUTERS = ['pylucid_migration.db_router.LegacyRouter']