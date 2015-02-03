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


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.dirname(os.path.dirname(__file__))


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


# Activate for PyLucid v1.x migration
# INSTALLED_APPS += (
#     "pylucid_migration",
# )


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'NAME': 'example_project.db',
        'PASSWORD': '',
        'HOST': 'localhost',
        'USER': '',
        'ENGINE': 'django.db.backends.sqlite3',
        'PORT': ''
    }
}