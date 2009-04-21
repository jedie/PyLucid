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

import pylucid_project
import pylucid_plugins

PYLUCID_PROJECT_ROOT = os.path.abspath(os.path.dirname(pylucid_project.__file__))
PYLUCID_PLUGINS_ROOT = os.path.abspath(os.path.dirname(pylucid_plugins.__file__))

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

SITE_ID = 1
ROOT_URLCONF = 'pylucid_project.urls'


_BASE_PATH = os.path.join(os.path.dirname(__file__))

_plugins = pylucid_plugins.PluginList(
    fs_path = os.path.join(_BASE_PATH, "pylucid_plugins"),
    pkg_prefix = "pylucid_project.pylucid_plugins"
)

TEMPLATE_DIRS = (
    os.path.join(_BASE_PATH, "apps/pylucid/templates/"),
    os.path.join(_BASE_PATH, "apps/pylucid_update/templates/"),
    
    os.path.join(_BASE_PATH, "apps/dbpreferences/templates/"),

    os.path.join(_BASE_PATH, "django/contrib/admin/templates"),
)
# Add all templates subdirs from all existing PyLucid plugins
TEMPLATE_DIRS += _plugins.get_template_dirs()

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

if DEBUG:
    # Display invalid (e.g. misspelled, unused) template variables
    # http://www.djangoproject.com/documentation/templates_python/#how-invalid-variables-are-handled
    # http://www.djangoproject.com/documentation/settings/#template-string-if-invalid
    TEMPLATE_STRING_IF_INVALID = "XXX INVALID TEMPLATE STRING '%s' XXX"


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    # PyLucid own apps:
    'pylucid_project.apps.pylucid',
    'pylucid_project.apps.pylucid_update', # Only needed for v0.8 users

    # external apps shipped and used with PyLucid:
    'dbpreferences',
    'dbtemplates',
    'reversion',
)
# Add all existing PyLucid plugins
INSTALLED_APPS += _plugins.get_installed_apps()
#print INSTALLED_APPS

#_____________________________________________________________________________
# PyLucid own settings

#from pylucid_project.apps.pylucid.app_settings import PYLUCID
from pylucid_project.apps.pylucid import app_settings as PYLUCID

ADMIN_URL_PREFIX = 'admin'

SITE_TEMPLATE_PREFIX = 'site_template/'


try:
    from local_settings import *
except ImportError:
    pass