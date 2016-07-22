# coding: utf-8

"""
    Django settings for example_project project
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Quick-start development settings - unsuitable for production:
        https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

    For more information on this file, see:
        https://docs.djangoproject.com/en/1.8/topics/settings/

    For the full list of settings and their values, see:
        https://docs.djangoproject.com/en/1.8/ref/settings/
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

TEMPLATES[0]["DIRS"].insert(0, os.path.join(PROJECT_DIR, 'templates'))


ROOT_URLCONF = 'example_project.urls'

WSGI_APPLICATION = 'example_project.wsgi.application'


INSTALLED_APPS += (
    'example_project',

    # Activate for PyLucid v1.x migration
    # "pylucid_migration",
    # "pylucid_todo",
)

# Your own djangocms-widgets templates:
WIDGET_TEMPLATES += (
    #('foo/bar.html', 'A foo bar example'),
)

#____________________________________________________________________
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'HOST': 'localhost',
        'PORT': '',
        'USER': '',
        'PASSWORD': '',
        'NAME': os.path.join(PROJECT_DIR, 'example_project.db'),
        'ATOMIC_REQUESTS': True,
    },
    # Activate for PyLucid v1.x migration:
    # 'legacy': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'HOST': 'localhost',
    #     'PORT': '',
    #     'USER': '',
    #     'PASSWORD': '',
    #     'NAME': 'PyLucid_v1_Database',
    #     'ATOMIC_REQUESTS': True,
    # }
}
# Activate for PyLucid v1.x migration
#DATABASE_ROUTERS = ['pylucid_migration.db_router.LegacyRouter']

#____________________________________________________________________
# Please change email-/SMTP-Settings:

# https://docs.djangoproject.com/en/1.8/ref/settings/#email-host
EMAIL_HOST = "localhost"
EMAIL_HOST_USER = "root@%s" % EMAIL_HOST
EMAIL_HOST_PASSWORD = ""

# https://docs.djangoproject.com/en/1.8/ref/settings/#default-from-email
# email address to use for various automated correspondence from the site manager(s). Except error mails:
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# https://docs.djangoproject.com/en/1.8/ref/settings/#server-email
# Email address that error messages come from:
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# https://docs.djangoproject.com/en/1.8/ref/settings/#managers
# A tuple that lists people who get broken link notifications when BrokenLinkEmailsMiddleware is enabled:
#MANAGERS = (('John', 'john@example.com'), ('Mary', 'mary@example.com'))

# https://docs.djangoproject.com/en/1.8/ref/settings/#admins
# A tuple that lists people who get code error notifications:
#ADMINS = MANAGERS


#____________________________________________________________________
# language setup
# note there are three places for language related settings:
#  * django
#  * djangocms
#  * django-parler (for djangocms-blog)
#
# see also: https://docs.djangoproject.com/en/1.8/topics/i18n/

# https://docs.djangoproject.com/en/1.8/ref/settings/#languages
LANGUAGES = (
    ('en', _('English')),
    ('de', _('German')),
)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# languages available in django CMS:
# http://docs.django-cms.org/en/latest/reference/configuration.html#std:setting-CMS_LANGUAGES
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

# https://docs.djangoproject.com/en/1.8/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "*", # Allow any domain/subdomain
    # 'www.example.tld',  # Allow domain
    # '.example.tld',  # Allow domain and subdomains
    # '.example.tld.',  # Also allow FQDN and subdomains
]

#____________________________________________________________________
# DEBUG

# *** SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
INTERNAL_IPS = (
    '127.0.0.1',
    '::1',
)


#____________________________________________________________________
# multisite
#
# See PyLucid README for more details!
#
# INSTALLED_APPS += (
#     'multisite',
#     'djangocms_multisite',
# )
#
# from multisite import SiteID
# SITE_ID = SiteID(default=1)
#
# CACHE_MULTISITE_ALIAS = 'multisite'
# CACHE_SITES_ALIAS = CACHE_MULTISITE_ALIAS # https://github.com/ecometrica/django-multisite/pull/34
# CACHES[CACHE_MULTISITE_ALIAS]= {
#     'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#     'TIMEOUT': 60 * 60 * 24,  # 24 hours
# }
#
# MULTISITE_FALLBACK="pylucid.multisite_views.auto_create_alias"
#
#
# MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
# _idx = MIDDLEWARE_CLASSES.index('cms.middleware.utils.ApphookReloadMiddleware')
# MIDDLEWARE_CLASSES.insert(_idx, 'multisite.middleware.DynamicSiteMiddleware')
# MIDDLEWARE_CLASSES.insert(_idx+2, 'djangocms_multisite.middleware.CMSMultiSiteMiddleware')
# MIDDLEWARE_CLASSES = tuple(MIDDLEWARE_CLASSES)
#
# MULTISITE_CMS_FALLBACK='www.example_project.com'
# MULTISITE_CMS_URLS={
#     MULTISITE_CMS_FALLBACK: ROOT_URLCONF,
#     #'www.example2.com': 'tests.test_utils.urls2',
# }
# MULTISITE_CMS_ALIASES={
#     MULTISITE_CMS_FALLBACK: (
#         'alias1.example_project.com', 'alias2.example_project.com',
#     ),
#     'www.example2.com': ('alias1.example2.com', 'alias2.example2.com',),
# }



#____________________________________________________________________
# extra DEBUG
#
# if DEBUG:
#     # Disable cache, for debugging:
#     CACHES['default']= {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#     }
#
#     INSTALLED_APPS += (
#         'debug_toolbar', # https://github.com/django-debug-toolbar/django-debug-toolbar
#         'django_info_panel', # https://github.com/jedie/django-debug-toolbar-django-info
#
#         # Add all models to django admin:
#         'pylucid_debug', # Must be the last App!
#     )
#     MIDDLEWARE_CLASSES = (
#         'debug_toolbar.middleware.DebugToolbarMiddleware',
#     ) + MIDDLEWARE_CLASSES



#____________________________________________________________________
# Work-a-round for:
# https://github.com/divio/django-cms/issues/5079
import sys
if "createcachetable" in sys.argv:
    INSTALLED_APPS = ()