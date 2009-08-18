# coding: utf-8

"""
    PyLucid.settings
    ~~~~~~~~~~~~~~~~

    Django settings for the PyLucid project.

    IMPORTANT:
        You should not edit this file!
        Owerwrite settings with a local settings file:
            local_settings.py

    Here are not all settings predifined you can use. Please look at the
    django documentation for a full list of all items:
        http://www.djangoproject.com/documentation/settings/

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

try:
    #from django_tools.utils import info_print;info_print.redirect_stdout()

    import pylucid_project
    from pylucid_project.system import pylucid_plugins
except Exception, e:
    import traceback
    print traceback.format_exc()
    raise

PYLUCID_PROJECT_ROOT = os.path.abspath(os.path.dirname(pylucid_project.__file__))
#PYLUCID_PLUGINS_ROOT = os.path.abspath(os.path.dirname(pylucid_plugins.__file__))

#______________________________________________________________________________
# SYS PATH SETUP

_path_list = (
#    PYLUCID_PLUGINS_ROOT,
    PYLUCID_PROJECT_ROOT,
    os.path.join(PYLUCID_PROJECT_ROOT, "apps")
)
for path in _path_list:
    if path not in sys.path:
        sys.path.insert(0, path)

#______________________________________________________________________________
# DEBUGGING

DEBUG = True

#______________________________________________________________________________
# DATABASE SETUP

# Database connection info.
DATABASE_ENGINE = 'sqlite3'    # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'test.db3'     # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


SITE_ID = 1 # Can be changed in local_settings


ROOT_URLCONF = 'pylucid_project.urls'

MIDDLEWARE_CLASSES = (
    'pylucid_project.middlewares.ip_ban.IPBanMiddleware',

    # From http://code.google.com/p/django-tools/
    'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'dbpreferences.middleware.DBPreferencesMiddleware',

    'pylucid_project.middlewares.page_msg.PageMessagesMiddleware',
    'pylucid_project.middlewares.pylucid_objects.PyLucidMiddleware',

    # slow down the django developer server
    # From http://code.google.com/p/django-tools/
#    'django_tools.middlewares.SlowerDevServer.SlowerDevServerMiddleware',
)
SLOWER_DEV_SERVER_SLEEP = 0.3 # time.sleep() value (in sec.)

PYLUCID_BASE_PATH = os.path.join(os.path.dirname(__file__))

_PYLUCID_PLUGIN_PACKAGES = (
    (os.path.join(PYLUCID_BASE_PATH, "pylucid_plugins"), "pylucid_project.pylucid_plugins"),
    #(os.path.join(PYLUCID_BASE_PATH, "external_plugins"), "pylucid_project.external_pylucid_plugins"),
)
pylucid_plugins.setup_plugins(_PYLUCID_PLUGIN_PACKAGES)

TEMPLATE_DIRS = (
    os.path.join(PYLUCID_BASE_PATH, "apps/pylucid/templates/"),
    os.path.join(PYLUCID_BASE_PATH, "apps/pylucid_admin/templates/"),
    os.path.join(PYLUCID_BASE_PATH, "apps/pylucid_update/templates/"),

    os.path.join(PYLUCID_BASE_PATH, "apps/dbpreferences/templates/"),

    os.path.join(PYLUCID_BASE_PATH, "django/contrib/admin/templates"),
)
# Add all templates subdirs from all existing PyLucid plugins
TEMPLATE_DIRS += pylucid_plugins.PYLUCID_PLUGINS.template_dirs
#print "settings.TEMPLATE_DIRS:", TEMPLATE_DIRS

TEMPLATE_LOADERS = (
    'dbtemplates.loader.load_template_source',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

# A tuple of callables that are used to populate the context in RequestContext.
# These callables take a request object as their argument and return a
# dictionary of items to be merged into the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "pylucid_project.apps.pylucid.context_processors.pylucid",
)

# Template debug should be off, because you didn't see a good debug page, if the error
# is in a lucidTag plugin view!
# Note that Django only displays fancy error pages if DEBUG is True!
TEMPLATE_DEBUG = False
#TEMPLATE_DEBUG = True

if DEBUG:
    # Display invalid (e.g. misspelled, unused) template variables
    # http://www.djangoproject.com/documentation/templates_python/#how-invalid-variables-are-handled
    # http://www.djangoproject.com/documentation/settings/#template-string-if-invalid
    # But note: Some django admin stuff is broken if TEMPLATE_STRING_IF_INVALID != ""
    # see also: http://code.djangoproject.com/ticket/3579
    # A work-a-round for this lives in ./pylucid_project/apps/pylucid_admin/admin.py 
    TEMPLATE_STRING_IF_INVALID = "XXX INVALID TEMPLATE STRING '%s' XXX"
#    from django_tools.template import warn_invalid_template_vars
#    warn_invalid_template_vars.add_warning()



INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.comments',

    # PyLucid own apps:
    'pylucid_project.apps.pylucid',
    'pylucid_project.apps.pylucid_admin',
    'pylucid_project.apps.pylucid_update', # Only needed for v0.8 users

    # external apps shipped and used with PyLucid:
    'dbpreferences',
    'dbtemplates',
    'reversion',
    'tagging',
)
# Add all existing PyLucid plugins
INSTALLED_APPS += pylucid_plugins.PYLUCID_PLUGINS.pkg_list
#print "settings.INSTALLED_APPS:", INSTALLED_APPS

COMMENTS_APP = "pylucid_project.pylucid_plugins.pylucid_comments"

#http://docs.djangoproject.com/en/dev/ref/settings/#setting-TEST_RUNNER
#Default: 'django.test.simple.run_tests'
TEST_RUNNER = 'pylucid_project.tests.test_tools.test_runner.run_tests'

#_____________________________________________________________________________
# PyLucid own settings

# Add app settings
try:
    from pylucid_project.apps.pylucid import app_settings as PYLUCID
    from pylucid_project.apps.pylucid_admin import app_settings as ADMIN
except Exception, e:
    import traceback
    print traceback.format_exc()
    raise


# http://www.djangoproject.com/documentation/authentication/#other-authentication-sources
AUTHENTICATION_BACKENDS = (
    "pylucid.system.auth_backends.SiteAuthBackend",
    "pylucid.system.auth_backends.SiteSHALoginAuthBackend",
#    "django.contrib.auth.backends.ModelBackend",
#    "pylucid_project.pylucid_plugins.auth.auth_backend.JS_SHA_Backend",
)
# http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
AUTH_PROFILE_MODULE = "pylucid.UserProfile"

#_____________________________________________________________________________
# STATIC FILES
# http://www.djangoproject.com/documentation/static_files/

# Serve static files for the development server?
# Using this method is inefficient and insecure.
# Do not use this in a production setting. Use this only for development.
SERVE_STATIC_FILES = False

# Note: Every URL/path...
# ...must be a absolute path.
# ...must have a trailing slash.

# Absolute _local_filesystem_path_ to the directory that holds media.
#     Example-1: "./media/" (default)
#     Example-2: "/home/foo/htdocs/media/"
MEDIA_ROOT = os.path.join(PYLUCID_BASE_PATH, "media") + "/"

# URL that handles the media served from MEDIA_ROOT.
#     Example-1: "/media/" (default)
#     Examlpe-2: "http://other_domain.net/media/"
#     Example-3: "http://media.your_domain.net/"
MEDIA_URL = "/media/"

# URL prefix for admin media -- CSS, JavaScript and images.
#     Examples-1: "/django/contrib/admin/media/" (default)
#     Examples-2: "http://other_domain.net/media/django/"
#     Examples-3: "http://django.media.your_domain.net/"
ADMIN_MEDIA_PREFIX = "/django/contrib/admin/media/"

# FIXME:
#LOGIN_REDIRECT_URL = "/?%s" % PYLUCID.AUTH_GET_VIEW
#LOGIN_URL = "/?%s" % PYLUCID.AUTH_GET_VIEW
#LOGOUT_URL = "/?%s" % PYLUCID.AUTH_LOGOUT_GET_VIEW


ADMIN_URL_PREFIX = 'admin'
PYLUCID_ADMIN_URL_PREFIX = 'pylucid_admin'


# TODO: must be used ;)
SLUG_BLACKLIST = (
    MEDIA_URL.strip("/").split("/", 1)[0],
    ADMIN_URL_PREFIX, PYLUCID_ADMIN_URL_PREFIX, PYLUCID.HEAD_FILES_URL_PREFIX,
)

# Prefix in filename, used for page templates and page styles
SITE_TEMPLATE_PREFIX = 'site_template/'


# The PyLucid install instrucion page:
INSTALL_HELP_URL = "http://pylucid.org/_goto/186/v0-9-testing/"




try:
    from local_settings import *
except ImportError:
    pass

