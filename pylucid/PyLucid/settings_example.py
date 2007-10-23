#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid.settings-example
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Django settings for the PyLucid project.

    1. You must copy this file:
            settings_example.py -> settings.py
    2. Change the basic settings.
        At least this: Database, _install section and middleware classes.

    Note, you must edit MIDDLEWARE_CLASSES, after installation!!!

    Here are not all settings predifined you can use. Please look at the
    django documentation for a full list of all items:
        http://www.djangoproject.com/documentation/settings/

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os


"""
_______________________________________________________________________________
 The Base settings, you should change:
"""

#______________________________________________________________________________
# DATABASE SETUP

# Database connection info.
DATABASE_ENGINE = 'sqlite3'    # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'PyLucid.db3'  # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Example for MySQL:
#DATABASE_ENGINE = 'mysql'
#DATABASE_NAME = 'DatabaseName'
#DATABASE_USER = 'UserName'
#DATABASE_PASSWORD = 'Password'
#DATABASE_HOST = 'localhost'
#DATABASE_PORT = '' # empty string for default port.


#_____________________________________________________________________________
# DEBUGGING

# deactivate the DEBUG mode in a productive environment because there a many
# information in a debug traceback ;)
# You should use INTERNAL_IPS to limit the access.
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Tuple of IP addresses, as strings, that:
#   * See debug comments, when DEBUG is true
#   * Receive x-headers
INTERNAL_IPS = ()

#_____________________________________________________________________________
# _INSTALL SECTION

# Install Password to login into the _install section.
ENABLE_INSTALL_SECTION = True
INSTALL_PASS_HASH = ""

#_____________________________________________________________________________
# MIDDLEWARE CLASSES

# List of middleware classes to use.  Order is important; in the request phase,
# this middleware classes will be applied in the order given, and in the
# response phase the middleware will be applied in reverse order.
#
# !!! IMPORTANT !!!
#  * In the first install phase (befor the database tables exists) the
#    'SessionMiddleware' and 'AuthenticationMiddleware' must be deactivated!
#  * After "syncdb" you must activate 'SessionMiddleware' and
#    'AuthenticationMiddleware'!
#  * The DebugPageCache should be *never* activated. Only for dev debugging.
# !!! IMPORTANT !!!
#
MIDDLEWARE_CLASSES = (
    # DebugPageCache normaly not used.
#    'PyLucid.middlewares.page_cache_debug.DebugPageCache',

    # Activate Session- and Authentication-Middleware after 'syncdb' :
    # -------------------------------------------------------------------------
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # -------------------------------------------------------------------------

    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.doc.XViewMiddleware',

    'PyLucid.middlewares.pagestats.PageStatsMiddleware',
)

# A secret key for this particular Django installation. Used in secret-key
# hashing algorithms. Set this in your settings, or Django will complain
# loudly.
# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

#_____________________________________________________________________________
# CACHE
#
# http://www.djangoproject.com/documentation/cache/
#
# In PyLucid every normal cms page request would be cached for anonymous users.
# For this cms page cache a working cache backend is needed.
#
# Note:
#    -You can test available backends in the _install section!
#
# Dummy caching ('dummy:///'):
#    The default non-caching. It just implements the cache interface without
#    doing anything.
#
# Database caching:
#    You must create the cache tables manually in the shell. Look at the django
#    cache documentation!
#
# Filesystem caching (e.g. 'file:///tmp'):
#    Usefull if memcache is not available. You should check if it allowed to
#    make temp files! You can test this in the PyLucid _install section!
#
# Local-memory caching ('locmem:///'):
#    Not useable with CGI! Every Request starts with a empty cache ;)
#    Waring: On shared webhosting, the available memory can be limited.
#
# Simple caching ('simple:///'):
#    It should only be used in development or testing environments.

# Default: "dummy:///" # (No caching)
CACHE_BACKEND = "dummy:///"

# The number of seconds each cms page should be cached.
CACHE_MIDDLEWARE_SECONDS = 600

#_____________________________________________________________________________
# STATIC FILES
# http://www.djangoproject.com/documentation/static_files/
#
# Note: Every URL/path...
# ...must be a absolute path.
# ...must have a trailing slash.

# Absolute _local_filesystem_path_ to the directory that holds media.
#     Example-1: "./media/" (default)
#     Example-2: "/home/foo/htdocs/media/"
MEDIA_ROOT = "./media/"


# URL that handles the media served from MEDIA_ROOT.
#     Example-1: "/media/" (default)
#     Examlpe-2: "http://other_domain.net/media/"
#     Example-3: "http://media.your_domain.net/"
MEDIA_URL = "/media/"


# URL for the PyLucid media files.
#     Example-1: "/media/PyLucid/" (default)
#     Examlpe-2: "http://other_domain.net/media/PyLucid/"
#     Example-3: "http://pylucid.media.your_domain.net/"
PYLUCID_MEDIA_URL = "/media/PyLucid/"


# URL prefix for admin media -- CSS, JavaScript and images.
#     Examples-1: "/django/contrib/admin/media/" (default)
#     Examples-2: "http://other_domain.net/media/django/"
#     Examples-3: "http://django.media.your_domain.net/"
ADMIN_MEDIA_PREFIX = "/django/contrib/admin/media/"

"""
_______________________________________________________________________________
 Advanced settings:
"""

# People who get code error notifications.
# In the format (('Full Name', 'email@domain.com'), ('Full Name', 'anotheremail@domain.com'))
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

# Not-necessarily-technical managers of the site. They get broken link
# notifications and other various e-mails.
MANAGERS = ADMINS

#_____________________________________________________________________________
# 404 BEHAVIOR

# tuple of strings that specify URLs that should be ignored by the 404 e-mailer.
# http://www.djangoproject.com/documentation/settings/#ignorable-404-ends
IGNORABLE_404_STARTS = ('/cgi-bin/',)
IGNORABLE_404_ENDS = ('favicon.ico', '.php')

#_____________________________________________________________________________
# I80N
# http://www.djangoproject.com/documentation/i18n/

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Chicago'


# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

#_____________________________________________________________________________
# EMAIL
# http://www.djangoproject.com/documentation/email/

# Default e-mail address to use for various automated correspondence
# Replace with a normal String like:
# DEFAULT_FROM_EMAIL = "webmaster@example.org"
DEFAULT_FROM_EMAIL = "webmaster@" + os.environ.get("HTTP_HOST", "localhost")

# Host for sending e-mail.
EMAIL_HOST = 'localhost'

# Port for sending e-mail.
EMAIL_PORT = 25

# Subject-line prefix for email messages send with django.core.mail.mail_admins
# or ...mail_managers.  Make sure to include the trailing space.
EMAIL_SUBJECT_PREFIX = '[PyLucid] '


#_____________________________________________________________________________
# SESSIONS

SESSION_COOKIE_NAME = 'sessionid'         # Cookie name. This can be whatever you want.
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2 # Age of cookie, in seconds (default: 2 weeks).
SESSION_COOKIE_DOMAIN = None              # A string like ".lawrence.com", or None for standard domain cookie.
SESSION_COOKIE_SECURE = False             # Whether the session cookie should be secure (https:// only).
SESSION_SAVE_EVERY_REQUEST = False        # Whether to save the session data on every request.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False   # Whether sessions expire when a user closes his browser.


#_____________________________________________________________________________
# TEMPLATE SYSTEM

# A tuple of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# A tuple of callables that are used to populate the context in RequestContext.
# These callables take a request object as their argument and return a
# dictionary of items to be merged into the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "PyLucid.system.context_processors.static",
)

# A tuple of locations of the template source files, in search order. Note that
# these paths should use Unix-style forward slashes, even on Windows.
TEMPLATE_DIRS = (
    "PyLucid/templates_django", "PyLucid/templates_PyLucid",
)


#_____________________________________________________________________________
# APP CONFIG


# A string representing the full Python import path to the PyLucid root URLconf.
ROOT_URLCONF = 'PyLucid.urls'

# A tuple of strings designating all applications that are enabled in this
# Django installation. Each string should be a full Python path to a Python
# package that contains a Django application
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    "PyLucid",
)


#_____________________________________________________________________________
# PYLUCID BASE SETTINGS
# basic adjustments, witch don't have to be changed.

# Path to the Plugins
PLUGIN_PATH = (
    {
        "type": "internal",
        "path": ("PyLucid", "plugins_internal"),
        "auto_install": True,
    },
    {
        "type": "external",
        "path": ("PyLucid", "plugins_external"),
        "auto_install": False,
    },
)

# special URL prefixes:

# Prefix for the install section
INSTALL_URL_PREFIX = "_install"
# Prefix for every command request
COMMAND_URL_PREFIX = "_command"
# Prefix to the django admin panel
ADMIN_URL_PREFIX = "_admin"


# static URLs (used in Traceback messages)

# The PyLucid install instrucion page:
INSTALL_HELP_URL = "http://www.pylucid.org/Documentation/install-PyLucid/"


# How are the DB initial database data stored?
INSTALL_DATA_DIR = 'PyLucid/db_dump_datadir'


# PyLucid cache prefix
PAGE_CACHE_PREFIX = "PyLucid_page_cache_"

# Additional Data Tag
# A temporary inserted Tag for Stylesheet and JavaScript data from the internal
# pages. Added by PyLucid.plugins_internal.page_style and replaces in
# PyLucid.index._replace_add_data()
ADD_DATA_TAG = "<!-- additional_data -->"

# JS-SHA1-Login Cookie name
INSTALL_COOKIE_NAME = "PyLucid_inst_auth"

# http://www.djangoproject.com/documentation/authentication/#other-authentication-sources
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "PyLucid.plugins_internal.auth.auth_backend.JS_SHA_Backend",
)

#_____________________________________________________________________________
# CHANGEABLE PYLUCID SETTINGS

# Enable the _install Python Web Shell Feature?
# Should be only enabled for tests. It is a big security hole!
INSTALL_EVILEVAL = False

# The table prefix from a old PyLucid installation, if exist.
# Only used for updating!
# Note: The OLD_TABLE_PREFIX can't be "PyLucid"!!!
OLD_TABLE_PREFIX = ""
# How to update a old v0.7.2 installation:
# 1. Backup you old installation (Save a SQL dump)!
# 2. init a fresh PyLucid installation. Follow the normal install steps:
# 2.1. install Db tables
# 2.2. init DB data
# 2.3. install internal plugins
# 3. convert the old content to the new installation:
# 3.1. update DB tables from v0.7.2 to django PyLucid v0.8
# 3.2. update to the new django template engine
# Use "low level admin/User administration" to set a new password for the user.

# Permit sending mails with the EMailSystem Plugin:
ALLOW_SEND_MAILS = True

# Every Plugin output gets a html SPAN tag around.
# Here you can defined witch CSS class name the tag should used:
CSS_PLUGIN_CLASS_NAME = "PyLucidPlugins"