# coding:utf-8

import os, tempfile

#
# Here a example local_settings.py
#
# At least you must specify STATIC_ROOT and DATABASES.
#
# see also:
# http://www.pylucid.org/permalink/332/a-complete-local_settingspy-example
#
BASE_PATH = os.path.abspath(os.path.dirname(__file__))


# Absolute _local_filesystem_path_ to the directory that holds media.
#
# STATIC_ROOT is for images, CSS, Javascript files that 
#             are needed to render a complete web page
# https://docs.djangoproject.com/en/1.4/ref/settings/#static-root
#
# MEDIA_ROOT is for user-uploaded media files (e.g. images)
# https://docs.djangoproject.com/en/1.4/ref/settings/#media-root
#
STATIC_ROOT = "/var/www/YourSite/static/"
MEDIA_ROOT = "/var/www/YourSite/media/"


# URL that handles the media served from STATIC_ROOT / MEDIA_ROOT
#     Example-1: "/static/" - "/media/" (default)
#     Example-2: "http://other_domain.net/static/"
#     Example-3: "http://static.your_domain.net/"
#
# Note: the URL mist have a trailing slash.
#
STATIC_URL = "/static/"
MEDIA_URL = "/media/"


# Changeable if needed (But should be off in productive usage!):
DEBUG = False
SQL_DEBUG = False
TEMPLATE_DEBUG = False

# Enable debug for one/some IP(s):
# https://docs.djangoproject.com/en/1.4/ref/settings/#internal-ips
INTERNAL_IPS = (
    # "123.456.789.012",
)


# Please insert your domains here:
# https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "*", # insert you domain and remove: "*"
    # '.example.com', # Allow domain and subdomains
    # '.example.com.', # Also allow FQDN and subdomains
]


# Database connection info.
# http://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup
# http://docs.djangoproject.com/en/dev/ref/settings/#setting-DATABASES
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_PATH, "test.db3") # You should use a absolute path to the SQlite file!
    }
}


SITE_ID = 1
LANGUAGE_CODE = "en"

# A secret key for this particular Django installation.
# Used to provide a seed in secret-key hashing algorithms.
# Set this to a random string -- the longer, the better.
SECRET_KEY = "add-a-secret-key"


# more info about CACHES setup here:
# http://www.pylucid.org/permalink/332/a-complete-local_settingspy-example#CACHES
#
#CACHE_MIDDLEWARE_SECONDS = 3600 # 1h
#
#_BACKEND = "django_tools.cache.smooth_cache_backends.SmoothFileBasedCache"
#_LOCATION_PREFIX = "/var/tmp/PyLucid_"
#CACHES = {
#    'default': {
#        'BACKEND': _BACKEND,
#        'LOCATION': _LOCATION_PREFIX + 'default-cache',
#        'TIMEOUT': CACHE_MIDDLEWARE_SECONDS,
#    },
#    'dbtemplates': {
#        'BACKEND': _BACKEND,
#        'LOCATION': _LOCATION_PREFIX + 'dbtemplates-cache',
#        'TIMEOUT': CACHE_MIDDLEWARE_SECONDS,
#    },
#    'LOCAL_SYNC_CACHE_BACKEND': {
#        'BACKEND': _BACKEND,
#        'LOCATION': _LOCATION_PREFIX + 'local_sync-cache',
#        'TIMEOUT': CACHE_MIDDLEWARE_SECONDS,
#    },
#}


# Please change email-/SMTP-Settings:

# http://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_HOST = "localhost"
EMAIL_HOST_USER = "root@%s" % EMAIL_HOST
EMAIL_HOST_PASSWORD = ""

# http://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# http://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Please uncomment and insert your mail and email address:
#MANAGERS = (('John', 'john@example.com'), ('Mary', 'mary@example.com'))
#ADMINS = MANAGERS

