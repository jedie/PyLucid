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
TEMPLATE_DIRS = (
    os.path.join(_BASE_PATH, "apps/pylucid/templates/"),
    os.path.join(_BASE_PATH, "apps/pylucid_update/templates/"),

    os.path.join(_BASE_PATH, "django/contrib/admin/templates"),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    #'pylucid_project.contrib.dbtemplates.loader.load_template_source',
)

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
    #'pylucid_project.contrib.dbtemplates',
)

#_____________________________________________________________________________
# PyLucid own settings

ADMIN_URL_PREFIX = 'admin'


try:
    from local_settings import *
except ImportError:
    pass