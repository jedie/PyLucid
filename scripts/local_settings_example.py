# coding:utf-8


#
# Here a example local_settings.py
#
# At least you must specify MEDIA_ROOT and DATABASES.
#
# see also:
# http://www.pylucid.org/permalink/332/a-complete-local_settingspy-example
#


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
        'NAME': 'test.db3' # You should set a absolute path to the SQlite file!
    }
}


SITE_ID = 1
LANGUAGE_CODE = "en"

# Set the Django cache system.
# The LocMemCache isn't memory-efficient. Should be changed!
# see: http://docs.djangoproject.com/en/dev/topics/cache/#setting-up-the-cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        #
        # e.g.:
        # IMPORTANT needs: >>> import os, tempfile <<< !!!
        #
        # 'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        # 'LOCATION': os.path.join(tempfile.gettempdir(), "PyLucid_cache_%s" % SITE_ID),       
    }
}
# Use the same cache in dbtemplates.
# You can also defined a different cache system.
# more information: http://django-dbtemplates.readthedocs.org/en/latest/advanced/#caching
CACHES["dbtemplates"] = CACHES["default"]

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


# Serve static files for the development server?
# Using this method is inefficient and insecure.
# Do not use this in a production setting!
# Only on for developer server!
SERVE_STATIC_FILES = False
