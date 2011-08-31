# coding:utf-8

import os, tempfile

#
# Here a example local_settings.py
#
# At least you must specify MEDIA_ROOT and DATABASES.
#
# see also:
# http://www.pylucid.org/permalink/332/a-complete-local_settingspy-example
#
BASE_PATH = os.path.abspath(os.path.dirname(__file__))


# Absolute _local_filesystem_path_ to the directory that holds media.
MEDIA_ROOT = "/var/www/YourSite/media/"


# URL that handles the media served from MEDIA_ROOT.
#     Example-1: "/media/" (default)
#     Examlpe-2: "http://other_domain.net/media/"
#     Example-3: "http://media.your_domain.net/"
MEDIA_URL = "/media/"


# URL prefix for django admin media -- CSS, JavaScript and images. Saved in /django/contrib/admin/media/
ADMIN_MEDIA_PREFIX = "/media/django/"


# Changeable if needed (But should be off in productive usage!):
DEBUG = False
SQL_DEBUG = False
TEMPLATE_DEBUG = False


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


# Set the Django cache system.
# The LocMemCache isn't memory-efficient. Should be changed!
# see: http://docs.djangoproject.com/en/dev/topics/cache/#setting-up-the-cache
#
# You can test if cache works, with:
#     PyLucid admin menu / system / base check
#
_CACHE_PATH_PREFIX = os.environ.get("USERNAME", "PyLucid")
# Change it with e.g. your username to make this cache "unique" on the server.
# This can be usefull on shared webhosting.
#
_CACHE_PATH_SUFFIX = str(SITE_ID)
# Must not changed.
#
_CACHE_PATH_MODE = 0700
# Default mode for cache directory is 0700 -> Useable only for current user.
# Change to 0777 if web process runs e.g. with nobody!
#
def _get_and_create_tempdir_location(entry):
    """
    Little helper for easy setup a cache filesystem path in temp.
    Try global temp directory, "tmp" in users's home or "tmp" in current working dir
    """
    possible_paths = (tempfile.gettempdir(), os.path.expanduser("~/tmp"), "tmp")
    sub_dir = "%s_%s_%s" % (_CACHE_PATH_PREFIX, entry, _CACHE_PATH_SUFFIX)
    for path in possible_paths:
        path = os.path.join(path, sub_dir)
        try:
            if not os.path.exists(path):
                os.makedirs(path, _CACHE_PATH_MODE)
            else:
                os.chmod(path, _CACHE_PATH_MODE)
        except:
            continue
        else:
            return path
    raise SystemError("Can't get a temp directory, tried: %s" % repr(possible_paths))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': _get_and_create_tempdir_location("default_cache"),
    },
    'dbtemplates': { # http://django-dbtemplates.readthedocs.org/en/latest/advanced/#caching
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': _get_and_create_tempdir_location("dbtemplates_cache"),
    },
    'local_sync_cache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': _get_and_create_tempdir_location("local_sync_cache"),
    }
}


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

