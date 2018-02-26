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


DOC_ROOT = "/path/to/page_instance/" # Point this to web server root directory

STATIC_ROOT = str(Path(DOC_ROOT, 'static'))
MEDIA_ROOT = str(Path(DOC_ROOT, 'media'))


PROJECT_DIR = Path(__file__).resolve().parent # Filesystem path to this instance

# Place for own templates:
TEMPLATES[0]["DIRS"] = [str(Path(PROJECT_DIR, "templates/"))]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "CHANGE ME!!!"


ROOT_URLCONF = 'example_project.urls'

WSGI_APPLICATION = 'example_project.wsgi.application'


# INSTALLED_APPS += (
#     #'example_project',
#
#     # Activate if old PyLucid migration was executed
#     # "pylucid_todo",
# )

# # Your own djangocms-widgets templates:
# WIDGET_TEMPLATES += (
#     #('foo/bar.html', 'A foo bar example'),
# )

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
        'NAME': str(Path(PROJECT_DIR, 'example_project.db')),
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
DEBUG = True

# https://github.com/jedie/django-tools#internalips---unix-shell-style-wildcards-in-internal_ips
from django_tools.settings_utils import InternalIps
INTERNAL_IPS = InternalIps(["127.0.0.1", "::1", "192.168.*.*", "10.0.*.*"])


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




