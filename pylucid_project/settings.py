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

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys


try:
    # from django_tools.utils import info_print;info_print.redirect_stdout()
    import django
    import dbpreferences  # http://code.google.com/p/django-dbpreferences/
    import django_tools  # http://code.google.com/p/django-tools/
    import django_processinfo  # https://github.com/jedie/django-processinfo
    import pylucid_project
    from pylucid_project.system.plugin_setup_info import PyLucidPluginSetupInfo
except Exception, e:
    import traceback
    sys.stderr.write(traceback.format_exc())
    raise


# include app settings from ./django_processinfo/app_settings.py
from django_processinfo import app_settings as PROCESSINFO


# Used by a few dynamic settings:
RUN_WITH_DEV_SERVER = "runserver" in sys.argv

def _pkg_path(obj):
    return os.path.abspath(os.path.dirname(obj.__file__))

# PYLUCID_BASE_PATH = os.path.abspath(os.path.dirname(pylucid_project.__file__))
PYLUCID_BASE_PATH = _pkg_path(pylucid_project)
DJANGO_BASE_PATH = _pkg_path(django)
# print "PYLUCID_BASE_PATH:", PYLUCID_BASE_PATH
# print "DJANGO_BASE_PATH:", DJANGO_BASE_PATH
# PYLUCID_PLUGINS_ROOT = os.path.abspath(os.path.dirname(pylucid_plugins.__file__))

# ______________________________________________________________________________
# SYS PATH SETUP

_path_list = (
#    PYLUCID_PLUGINS_ROOT,
    PYLUCID_BASE_PATH,
    os.path.join(PYLUCID_BASE_PATH, "apps")
)
for path in _path_list:
    if path not in sys.path:
        sys.path.insert(0, path)

# ______________________________________________________________________________
# DEBUGGING

DEBUG = False

# Append all SQL queries into the html page. (Works only if DEBUG==True)
# Should allways be False. It's only for developing!
SQL_DEBUG = False

# See if request.PYLUCID attributes attached or changes (Works only if DEBUG==True)
# See also: http://www.pylucid.org/permalink/133/pylucid-objects#DEBUG
# Should allways be False. It's only for developing!
PYLUCID_OBJECTS_DEBUG = False

# We must set a default DB settings here, otherwise management commands doesn't work.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'PleaseOverwrite_DATABASES_settings',
    }
}

SITE_ID = 1  # Can be changed in local_settings


ROOT_URLCONF = 'pylucid_project.urls'


# activate django-tools DynamicSiteMiddleware:
USE_DYNAMIC_SITE_MIDDLEWARE = True

MIDDLEWARE_CLASSES = (
    # Save process informations. More info: https://github.com/jedie/django-processinfo
    'django_processinfo.middlewares.django_processinfo.ProcessInfoMiddleware',

    # Set request.debug bool value:
    'django_tools.debug.middlewares.SetRequestDebugMiddleware',

    # Block banned IP addresses and delete old pylucid.models.BanEntry items:
    'pylucid_project.middlewares.ip_ban.IPBanMiddleware',

    # Insert a statistic line into the generated page:
    'pylucid_project.middlewares.pagestats.PageStatsMiddleware',

    # Calls check_state() for every "Local sync cache" to reset out-dated caches
    'django_tools.local_sync_cache.LocalSyncCacheMiddleware.LocalSyncCacheMiddleware',

    # make the request object everywhere available with a thread local storage:
    'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',

    # Set SITE_ID dynamically base on the current domain name:
    'django_tools.dynamic_site.middleware.DynamicSiteMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',

    # https://github.com/jedie/django-tools/blob/master/django_tools/cache/README.creole
    'django_tools.cache.site_cache_middleware.UpdateCacheMiddleware',
    'django_tools.cache.site_cache_middleware.FetchFromCacheMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Create request.user_settings at process_request() and save it on process_response():
    'dbpreferences.middleware.DBPreferencesMiddleware',

    # Create request.PYLUCID and log process_exception():
    'pylucid_project.middlewares.pylucid_objects.PyLucidMiddleware',

    # slow down the django developer server
    # From http://code.google.com/p/django-tools/
#    'django_tools.middlewares.SlowerDevServer.SlowerDevServerMiddleware',

    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',

    'reversion.middleware.RevisionMiddleware',

    # Insert a html link anchor to all headlines:
    'pylucid_project.middlewares.headline_anchor.HeadlineAnchorMiddleware',

    # Set django message level by user type and system preferences:
    'pylucid_project.middlewares.message_level.MessageLevelMiddleware',

    # For PyLucid context middlewares API, see: http://www.pylucid.org/permalink/134/new-v09-plugin-api#context-middleware
    "pylucid_project.middlewares.context_middlewares.PyLucidContextMiddlewares",
)

# For django_tools.cache.site_cache_middleware
# https://github.com/jedie/django-tools/blob/master/django_tools/cache/README.creole
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True  # Don't use cache for authenticated users

# Add stack information to every messages, but only if..
#     ...settings.DEBUG == True
# or
#     ...settings.MESSAGE_DEBUG == True
MESSAGE_STORAGE = "django_tools.utils.messages.StackInfoStorage"


# initialized all pylucid plugins
PYLUCID_PLUGIN_SETUP_INFO = PyLucidPluginSetupInfo(
    plugin_package_list=(
        (PYLUCID_BASE_PATH, "pylucid_project", "apps"),  # base apps
        (PYLUCID_BASE_PATH, "pylucid_project", "pylucid_plugins"),
        (PYLUCID_BASE_PATH, "pylucid_project", "external_plugins"),
    ),
#    verbose=True
    verbose=False
)


# Add all templates subdirs from all existing PyLucid apps + plugins
TEMPLATE_DIRS = PYLUCID_PLUGIN_SETUP_INFO.template_dirs

# Append "static" template directories:
TEMPLATE_DIRS += (
    os.path.join(_pkg_path(django_tools), "templates/"),
    os.path.join(_pkg_path(dbpreferences), "templates/"),
    os.path.join(_pkg_path(django_processinfo), "templates/"),

    os.path.join(_pkg_path(django), "contrib/admin/templates"),
)
# print "settings.TEMPLATE_DIRS:\n", "\n".join(TEMPLATE_DIRS)


TEMPLATE_LOADERS = (
    'dbtemplates.loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# A tuple of callables that are used to populate the context in RequestContext.
# These callables take a request object as their argument and return a
# dictionary of items to be merged into the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",  # Add request object to context
    "django.core.context_processors.static",  # Add STATIC_URL to context
    "django.core.context_processors.media",  # Add MEDIA_URL to context
    "django.contrib.messages.context_processors.messages",
    "pylucid_project.apps.pylucid.context_processors.pylucid",
)

# Template debug should be off, because you didn't see a good debug page, if the error
# is in a lucidTag plugin view!
# Note that Django only displays fancy error pages if DEBUG is True!
TEMPLATE_DEBUG = False
# TEMPLATE_DEBUG = True

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
    'django.contrib.redirects',
    'django.contrib.staticfiles',

    # PyLucid own apps:
    'pylucid_project.apps.pylucid',
    'pylucid_project.apps.pylucid_admin',
    'pylucid_project.apps.pylucid_update',  # Only needed for v0.8 users

    # external apps shipped and used with PyLucid:
	'django_tools.dynamic_site',  # https://github.com/jedie/django-tools/blob/master/django_tools/dynamic_site/README.creole
    'dbpreferences',  # http://code.google.com/p/django-dbpreferences/
    'dbtemplates',  # http://code.google.com/p/django-dbtemplates/
    'reversion',  # http://code.google.com/p/django-reversion/
    'reversion_compare',  # https://github.com/jedie/django-reversion-compare
    'tagging',  # http://code.google.com/p/django-tagging/
    'compressor',  # https://github.com/jezdez/django_compressor
    'south',  # http://south.aeracode.org/
    'django_processinfo',  # https://github.com/jedie/django-processinfo
)

# Temp. work-a-round for https://github.com/jezdez/django-dbtemplates/pull/31
# TODO: remove until new django-dbtemplates release exist with the bugfix.
DATABASE_ENGINE = "XXX"

# Add all existing PyLucid apps + plugins
INSTALLED_APPS += PYLUCID_PLUGIN_SETUP_INFO.installed_plugins
# print "settings.INSTALLED_APPS:", "\n".join(INSTALLED_APPS)

COMMENTS_APP = "pylucid_project.pylucid_plugins.pylucid_comments"

# http://docs.djangoproject.com/en/dev/ref/settings/#setting-TEST_RUNNER
# Default: 'django.test.simple.run_tests'
TEST_RUNNER = 'pylucid_project.tests.test_tools.test_runner.PyLucidTestRunner'

if RUN_WITH_DEV_SERVER:
    # print mails to console if dev server used.
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    ADMINS = (
        ("test", "dev_server_test@example_domain.tld"),
    )

# _____________________________________________________________________________
# PyLucid own settings

# Add app settings
try:
    from pylucid_project.apps.pylucid import app_settings as PYLUCID
    from pylucid_project.apps.pylucid_admin import app_settings as ADMIN
except Exception, e:
    import traceback
    sys.stderr.write(traceback.format_exc())
    raise


# http://www.djangoproject.com/documentation/authentication/#other-authentication-sources
AUTHENTICATION_BACKENDS = (
    "pylucid_project.pylucid_plugins.auth.auth_backends.SiteAuthBackend",
    "pylucid_project.pylucid_plugins.auth.auth_backends.SiteSHALoginAuthBackend",
#    "django.contrib.auth.backends.ModelBackend",
)
# http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
AUTH_PROFILE_MODULE = "pylucid.UserProfile"

# _____________________________________________________________________________
# STATIC FILES
#
# must be set in local_settings.py
# would be checked at the end of this file
#
STATIC_ROOT = None
STATIC_URL = None
MEDIA_ROOT = None
MEDIA_URL = None

# https://docs.djangoproject.com/en/1.4/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = ()

# Set base path for include plugin:
# http://www.pylucid.org/permalink/381/about-the-include-plugin
PYLUCID_INCLUDE_BASEPATH = None

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # django-compressor:
    'compressor.finders.CompressorFinder',
)

# Enable django-compressor even if DEBUG is on:
COMPRESS_ENABLED = True


ADMIN_URL_PREFIX = 'admin'
PYLUCID_ADMIN_URL_PREFIX = 'pylucid_admin'

LOGIN_REDIRECT_URL = "/%s/" % ADMIN_URL_PREFIX
LOGIN_URL = "/%s/" % ADMIN_URL_PREFIX
LOGOUT_URL = "/?%s" % PYLUCID.AUTH_LOGOUT_GET_VIEW

# Blacklist of PageTree slugs that are not useable.
# Would be extendet at the end of this file!
SLUG_BLACKLIST = (
    ADMIN_URL_PREFIX, PYLUCID_ADMIN_URL_PREFIX, PYLUCID.HEAD_FILES_URL_PREFIX,
)

# Prefix in filename, used for page templates
SITE_TEMPLATE_PREFIX = 'site_template'

# Prefix in filename, used for page stylesheet
SITE_STYLE_PREFIX = 'site_stylesheet'


# Django can't handling time zone very good.
# The Django default TIME_ZONE is 'America/Chicago' (Central Standard Time Zone, (CST), UTC-6)
# but this is not the best choice.
# We set it to "UTC" (same as Greenwich Mean Time, GMT-0, without daylight-saving time)
# All datetime (e.g. model createtime) would be stored in UTC.
# See also: http://groups.google.com/group/django-developers/browse_thread/thread/4ca560ef33c88bf3
TIME_ZONE = "UTC"

# Default system language.
# (Default from django is en-us, but this doesn't exist in PyLucid installed data)
LANGUAGE_CODE = "en"

# https://docs.djangoproject.com/en/1.3/ref/settings/#std:setting-LOCALE_PATHS
LOCALE_PATHS = (
    os.path.join(PYLUCID_BASE_PATH, "apps", "pylucid", "locale"),
)
USE_I18N = True

# _______________________________________________________________________________
# dbtemplates settings
# http://packages.python.org/django-dbtemplates/overview.html#settings

# dbtemplate should used django-reversion
DBTEMPLATES_USE_REVERSION = True

# _______________________________________________________________________________
# settings for local_sync_cache from django-tools

if DEBUG and RUN_WITH_DEV_SERVER:
    LOCAL_SYNC_CACHE_DEBUG = True
else:
    LOCAL_SYNC_CACHE_DEBUG = False

LOCAL_SYNC_CACHE_BACKEND = "local_sync_cache"

# _______________________________________________________________________________
# Set the Django cache system.

CACHE_MIDDLEWARE_SECONDS = 3600  # 1h

# The LocMemCache isn't memory-efficient. Should be changed in local_settings.py !
_BACKEND = "django_tools.cache.smooth_cache_backends.SmoothLocMemCache"
CACHES = {
    'default': {
        'BACKEND': _BACKEND,
        'LOCATION': 'PyLucid-default-cache',
        'TIMEOUT': CACHE_MIDDLEWARE_SECONDS,
    },
    'dbtemplates': {  # http://django-dbtemplates.readthedocs.org/en/latest/advanced/#caching
        'BACKEND': _BACKEND,
        'LOCATION': 'PyLucid-dbtemplates-cache',
        'TIMEOUT': CACHE_MIDDLEWARE_SECONDS,
    },
    LOCAL_SYNC_CACHE_BACKEND: {  # https://github.com/jedie/django-tools/blob/master/django_tools/local_sync_cache/local_sync_cache.py
        'BACKEND': _BACKEND,
        'LOCATION': 'PyLucid-local_sync-cache',
        'TIMEOUT': CACHE_MIDDLEWARE_SECONDS,
    },
}

# _______________________________________________________________________________

# unittest running?
_IN_UNITTESTS = "PYLUCID_UNITTESTS" in os.environ or "test" in sys.argv

if _IN_UNITTESTS:
    # For running unittests with sqlite and south:
    # http://south.aeracode.org/wiki/Settings#SOUTH_TESTS_MIGRATE
    SOUTH_TESTS_MIGRATE = False


# Must be set in local settings
ALLOWED_HOSTS = None

# Must be set in local settings
SECRET_KEY = None

# _______________________________________________________________________________
# include additional_settings from plugins

PYLUCID_PLUGIN_SETUP_INFO.get_additional_settings(locals())

# _______________________________________________________________________________
# overwrite values from the local settings

def _error(msg):
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(msg)

LOCAL_SETTINGS_MODULE = os.environ.get("LOCAL_SETTINGS_MODULE", "local_settings")

try:
    # from local_settings import *
    _local_settings = __import__(LOCAL_SETTINGS_MODULE, globals(), locals(), ["*"])
except ImportError, err:
    if str(err).startswith("No module named"):
        msg = (
            "There is no %s.py file in '%s' !"
            " (Original error was: %s)\n"
        ) % (LOCAL_SETTINGS_MODULE, os.getcwd(), err)
        _error(msg)
    else:
        raise

# Only for information:
LOCAL_SETTINGS_MODULE_PATH = _local_settings.__file__

# assimilate all local settings from modul, see: http://stackoverflow.com/a/2916810/746522
for key in dir(_local_settings):
    if not key.startswith("_"):
        locals()[key] = getattr(_local_settings, key)

del(_local_settings)


# _______________________________________________________________________________
# check some settings

if not "create_instance" in sys.argv:
    if SECRET_KEY in (None, ""):
        _error("You must set a SECRET_KEY in your local_settings.py!")

    if ALLOWED_HOSTS in (None, ""):
        _error("You must set a ALLOWED_HOSTS in your local_settings.py!")

    if DEBUG or RUN_WITH_DEV_SERVER:
        # Check all STATICFILES_DIRS
        for dir in STATICFILES_DIRS:
            if not os.path.isdir(dir):
                _error("Directory in STATICFILES_DIRS doesn't exist: %r" % dir)

    # __________________________________________________________________________
    # Check STATIC_* and MEDIA_*

    def _check_if_set(info, value):
        if not value:
            _error("%s must be set in local_settings.py !" % info)

    def _check_path(info, path):
        _check_if_set(info, path)
        if not os.path.exists(path):
            _error("%s %r doesn't exists!" % (info, path))

    _check_path("STATIC_ROOT", STATIC_ROOT)
    _check_path("MEDIA_ROOT", MEDIA_ROOT)

    _check_if_set("STATIC_URL", STATIC_URL)
    _check_if_set("MEDIA_URL", MEDIA_URL)

    del(_check_path)
    del(_check_if_set)

    # __________________________________________________________________________
    # expand SLUG_BLACKLIST

    SLUG_BLACKLIST = list(SLUG_BLACKLIST)

    if "." not in STATIC_URL:
        # URL is not a other domain / sub domain
        SLUG_BLACKLIST.append(STATIC_URL.strip("/").split("/", 1)[0])

    if "." not in MEDIA_URL:
        SLUG_BLACKLIST.append(MEDIA_URL.strip("/").split("/", 1)[0])

    SLUG_BLACKLIST = tuple([item.lower() for item in SLUG_BLACKLIST])

del(_error)
