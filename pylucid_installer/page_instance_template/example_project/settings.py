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

from django.utils.translation import ugettext_lazy as _

# Load the PyLucid base settings
from pylucid.base_settings import *


DOC_ROOT = "/path/to/page_instance/" # Point this to webserver root directory
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "CHANGE ME!!!"

MEDIA_ROOT = os.path.join(DOC_ROOT, 'media')
STATIC_ROOT = os.path.join(DOC_ROOT, 'static')

STATICFILES_DIRS = (
    # Activate this, if you have own static files:
    #os.path.join(PROJECT_DIR, 'static'),
)
TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
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


#____________________________________________________________________
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'NAME': os.path.join(PROJECT_DIR, 'example_project.db'),
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


#____________________________________________________________________
# language setup
# note there are three places for language related settings:
#  * django
#  * djangocms
#  * django-parler (for djangocms-blog)
#
# see also: https://docs.djangoproject.com/en/1.7/topics/i18n/

# https://docs.djangoproject.com/en/1.7/ref/settings/#languages
LANGUAGES = (
    ('en', _('English')),
    ('de', _('German')),
)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# languages available in django CMS:
# http://docs.django-cms.org/en/stable/reference/configuration.html#std:setting-CMS_LANGUAGES
CMS_LANGUAGES = {
    'default': { # all SITE_ID's
        'fallbacks': ['en', 'de'],
        'redirect_on_fallback': True,
        'public': True,
        'hide_untranslated': False,
    },
    # 1: [ # SITE_ID == 1
    #     {
    #         'redirect_on_fallback': True,
    #         'public': True,
    #         'hide_untranslated': False,
    #         'code': 'en',
    #         'name': _('English'),
    #     },
    #     {
    #         'redirect_on_fallback': True,
    #         'public': True,
    #         'hide_untranslated': False,
    #         'code': 'de',
    #         'name': _('Deutsch'),
    #     },
    # ],
}

# http://django-parler.readthedocs.org/en/latest/quickstart.html#configuration
PARLER_DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE
PARLER_LANGUAGES = {
    None: (
        {'code': 'en',},
        {'code': 'de',},
    ),
    # 1: ( # SITE_ID == 1
    #     {'code': 'en',},
    #     {'code': 'de',},
    # ),
    # 2: ( # SITE_ID == 2
    #     {'code': 'en',},
    #     {'code': 'de',},
    # ),
    'default': {
        'fallback': PARLER_DEFAULT_LANGUAGE_CODE,
        'hide_untranslated': False,   # the default; let .active_translations() return fallbacks too.
    }
}

# https://docs.djangoproject.com/en/1.7/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "*", # Allow any domain/subdomain
    # 'www.example.tld',  # Allow domain
    # '.example.tld',  # Allow domain and subdomains
    # '.example.tld.',  # Also allow FQDN and subdomains
]

#____________________________________________________________________
# DEBUG

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False
INTERNAL_IPS = (
    '127.0.0.1',
    '::1',
)

# Disable cache, for debugging:
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#     }
# }

# django-debug-toolbar - https://github.com/django-debug-toolbar/django-debug-toolbar
# INSTALLED_APPS += (
#     'debug_toolbar',
# )
# MIDDLEWARE_CLASSES = (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ) + MIDDLEWARE_CLASSES