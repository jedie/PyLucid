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
        'NAME': 'test.db3'
    }
}


SITE_ID = 1
LANGUAGE_CODE = "en"

CACHE_BACKEND = 'file:///tmp/PyLucid_cache_%s' % SITE_ID


# Please uncomment and insert your name/email:
#MANAGERS = (('John', 'john@example.com'), ('Mary', 'mary@example.com'))
#ADMINS = MANAGERS


# Serve static files for the development server?
# Using this method is inefficient and insecure.
# Do not use this in a production setting!
# Only on for developer server!
SERVE_STATIC_FILES = False
