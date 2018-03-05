# coding: utf-8

"""
    PyLucid base settings
    ~~~~~~~~~~~~~~~~~~~~~
"""

from pathlib import Path

from django.utils.translation import ugettext_lazy as _


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SITE_ID=1


from django_tools.settings_utils import FnMatchIps

# Required for the debug toolbar to be displayed:
INTERNAL_IPS = FnMatchIps(["localhost", "127.0.0.1", "::1", "172.*.*.*", "192.168.*.*", "10.0.*.*"])

ALLOWED_HOSTS = INTERNAL_IPS


# Application definition

INSTALLED_APPS = (
    'djangocms_admin_style', # must be inserted before django.contrib.admin

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'debug_toolbar', # https://github.com/jazzband/django-debug-toolbar/

    'compressor', # https://github.com/django-compressor/django-compressor

    'cms', # https://github.com/divio/django-cms
    'menus', # Part of Django-CMS

    'djangocms_history', # https://github.com/divio/djangocms-history

    'treebeard', # https://github.com/django-treebeard/django-treebeard
    'sekizai', # https://github.com/ojii/django-sekizai
    'djangocms_text_ckeditor', # https://github.com/divio/djangocms-text-ckeditor

    # TODO: remove if migration from 'cmsplugin_filer_link' to 'djangocms-link' is done:
    # http://docs.django-cms.org/en/latest/topics/commonly_used_plugins.html#deprecated-addons
    'cmsplugin_filer_link',

    'cmsplugin_pygments', # https://github.com/chrisglass/cmsplugin-pygments
    'cmsplugin_markup', # https://github.com/mitar/cmsplugin-markup

    'djangocms_htmlsitemap', # https://github.com/kapt-labs/djangocms-htmlsitemap

    # djangocms-blog dependencies, see: https://djangocms-blog.readthedocs.io/en/latest/installation.html
    'filer', # https://github.com/divio/django-filer
    'easy_thumbnails', # https://github.com/SmileyChris/easy-thumbnails
    'aldryn_apphooks_config',
    'cmsplugin_filer_image',
    'parler', # https://pypi.org/project/django-parler
    'taggit',
    'taggit_autosuggest',
    'meta', # https://github.com/nephila/django-meta
    'djangocms_blog',


    # https://github.com/jedie/django-cms-tools/
    'django_cms_tools',
    'django_cms_tools.filer_tools',
    'django_cms_tools.plugin_anchor_menu',
    # 'django_cms_tools.plugin_landing_page', # TODO: Needs publisher!

    'pylucid',
    # 'pylucid_todo', # Only needed for old migrated installations

    # Installed only in developer installation:
    #'django_extensions', # https://github.com/django-extensions/django-extensions
)

ROOT_URLCONF = 'pylucid_page_instance.urls'
WSGI_APPLICATION = 'pylucid_page_instance.wsgi.application'

MIDDLEWARE = (
    'django.middleware.cache.UpdateCacheMiddleware',

    # https://github.com/jazzband/django-debug-toolbar/
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'loaders': [
                ('django.template.loaders.cached.Loader', (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )),
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.static',
                'cms.context_processors.cms_settings',
                'pylucid.context_processors.pylucid',
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# Must be set in page instance settings:
DATABASES = {}


# https://docs.djangoproject.com/en/1.11/topics/cache/#database-caching
import sys
if sys.argv[0].endswith("test") or "pytest" in sys.argv or "test" in sys.argv:
    print("Use 'LocMemCache' CACHES in tests, because of:")
    print("https://github.com/divio/django-cms/issues/5079")
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
else:
    #
    # The cache tables must be created first, e.g.:
    #   $ manage.py createcachetable
    #
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'pylucid_cache_table',
        },
    }

# Hack needed, until https://github.com/divio/django-cms/issues/5079 is fixed:
if "createcachetable" in sys.argv:
    INSTALLED_APPS = list(INSTALLED_APPS)
    INSTALLED_APPS.remove("cms")
    INSTALLED_APPS.remove("djangocms_blog")


# https://django-compressor.readthedocs.io/en/latest/settings/
#COMPRESS_ENABLED=False
COMPRESS_ENABLED=True


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# Default and fallback language:
# https://docs.djangoproject.com/en/1.11/ref/settings/#language-code
LANGUAGE_CODE = "en"

# http://docs.django-cms.org/en/latest/reference/configuration.html#std:setting-CMS_LANGUAGES
CMS_LANGUAGES = {
    1: [
        {
            "name": _("English"),
            "code": "en",
            "fallbacks": ["de"],
            "redirect_on_fallback":True,
            "public": True,
            "hide_untranslated": False,
        },
        {
            "name": _("German"),
            "code": "de",
            "fallbacks": ["en"],
            "redirect_on_fallback":True,
            "public": True,
            "hide_untranslated": False,
        },
    ],
    "default": { # all SITE_ID"s
        "fallbacks": [LANGUAGE_CODE],
        "redirect_on_fallback":True,
        "public": True,
        "hide_untranslated": False,
    },
}

# https://django-parler.readthedocs.io/en/latest/api/parler.utils.conf.html#parler.utils.conf.get_parler_languages_from_django_cms
# PARLER_LANGUAGES will be generated from CMS_LANGUAGES since parler v1.6


# https://docs.djangoproject.com/en/1.11/ref/settings/#languages
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGES = tuple([(d["code"], d["name"]) for d in CMS_LANGUAGES[1]])

LANGUAGE_DICT = dict(LANGUAGES) # useful to get translated name by language code

# http://django-parler.readthedocs.org/en/latest/quickstart.html#configuration
PARLER_DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE


TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Must be set in settings from page instance:
# STATIC_ROOT =
# MEDIA_ROOT =


# https://django-debug-toolbar.readthedocs.io/en/stable/configuration.html#debug-toolbar-config
from debug_toolbar.settings import CONFIG_DEFAULTS as DEBUG_TOOLBAR_CONFIG

# don't load jquery from ajax.googleapis.com, just use django's version:
DEBUG_TOOLBAR_CONFIG["JQUERY_URL"] = STATIC_URL + "admin/js/vendor/jquery/jquery.min.js"


# Basic Django CMS settings

CMS_TEMPLATES = (
    ('pylucid/bootstrap/split_tree_menu_left.html', 'Split tree menu left'),
    ('pylucid/bootstrap/fullwidth.html', 'Top menu - full width'),
    ('pylucid/bootstrap/sidebar_left.html', 'Top menu with sidebar left'),
    ('pylucid/bootstrap/homepage.html', 'Homepage template'),
    ('pylucid/bootstrap/tree_menu_left.html', 'Tree menu left'),
    ('pylucid/bootstrap/tree_menu_right.html', 'Tree menu right'),
    ('pylucid/simple.html', 'Simple'),
    # ('base.html', 'Basic Page'),
)

# http://docs.django-cms.org/en/latest/reference/configuration.html#cms-permission
CMS_PERMISSION = False

# Basic Placeholder config

# from djangocms_text_ckeditor.cms_plugins import TextPlugin
CKEDITOR = "TextPlugin"

from django_cms_tools.plugin_anchor_menu import constants as plugin_anchor_menu_constants

CMS_PLACEHOLDER_CONF = {
    None: {
        'name': _("Content"),
        'plugins': [
            CKEDITOR,
            plugin_anchor_menu_constants.ANCHOR_PLUGIN_NAME,
            plugin_anchor_menu_constants.DROP_DOWN_ANCHOR_MENU_PLUGIN_NAME,
        ],
        'default_plugins': [
            {
                'plugin_type': CKEDITOR,
                'values':{'body':'<p>(There is no content, yet.)</p>'},
            },
        ],
    },
}

# https://djangocms-blog.readthedocs.io/en/latest/installation.html#minimal-configuration
META_SITE_PROTOCOL = 'http' # Should be changed to "https" in production!
META_USE_SITES = True


# http://django-filer.readthedocs.org/en/latest/installation.html#configuration
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)


#_____________________________________________________________________________
# https://github.com/mitar/cmsplugin-markup
CMS_MARKUP_OPTIONS = (
    'cmsplugin_markup.plugins.creole',
    'cmsplugin_markup.plugins.html',
    'cmsplugin_markup.plugins.markdown',
    'cmsplugin_markup.plugins.textile',
    'cmsplugin_markup.plugins.restructuredtext',
)
CMS_MARKUP_RENDER_ALWAYS = True
CMS_MARKDOWN_EXTENSIONS = ()


#_____________________________________________________________________________
# cut 'pathname' in log output

import logging

old_factory = logging.getLogRecordFactory()


def cut_path(pathname, max_length):
    if len(pathname)<=max_length:
        return pathname
    return "...%s" % pathname[-(max_length-3):]


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.cut_path = cut_path(record.pathname, 30)
    return record


logging.setLogRecordFactory(record_factory)


# -----------------------------------------------------------------------------


# https://docs.python.org/3/library/logging.html#logging-levels
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)8s %(cut_path)s:%(lineno)-3s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django_tools': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django_cms_tools': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'pylucid': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
