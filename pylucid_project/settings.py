
import os

DEBUG = True

#______________________________________________________________________________
# DATABASE SETUP

# Database connection info.
DATABASE_ENGINE = 'sqlite3'    # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'test_pylucid_v0.8.db3'  # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

SITE_ID = 1
ROOT_URLCONF = 'pylucid_project.urls'

_BASE_PATH = os.path.join(os.path.dirname(__file__))
TEMPLATE_DIRS = (
    os.path.join(_BASE_PATH, "apps/pylucid/templates/"),
    
    os.path.join(_BASE_PATH, "django/contrib/admin/templates"),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'apps.pylucid',
)

#_____________________________________________________________________________
# PyLucid own settings

ADMIN_URL_PREFIX = 'admin'
