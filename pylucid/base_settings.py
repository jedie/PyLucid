# coding: utf-8

"""
    PyLucid base settings
    ~~~~~~~~~~~~~~~~~~~~~

    see also:
    https://github.com/django/django/blob/master/django/conf/global_settings.py
    https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy as _
# _ = lambda s: s


ALLOWED_HOSTS = []


TIME_ZONE = 'America/Chicago'

USE_I18N = True
USE_L10N = True

# If you set this to True, Django will use timezone-aware datetimes:
USE_TZ = False



SITE_ID = 1

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.csrf',
    'django.core.context_processors.tz',
    'sekizai.context_processors.sekizai',
    'django.core.context_processors.static',
    'cms.context_processors.cms_settings'
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'cms',
    'djangocms_admin_style',
    'djangocms_text_ckeditor',
    'menus',
    'sekizai',
    'mptt',
    # 'djangocms_style',
    # 'djangocms_column',
    'djangocms_file',
    # 'djangocms_flash',
    # 'djangocms_googlemap',
    # 'djangocms_inherit',
    'djangocms_link',
    'djangocms_picture',
    # 'djangocms_teaser',
    'djangocms_video',
    'cmsplugin_htmlsitemap', # https://github.com/raphaa/cmsplugin-htmlsitemap
    'cmsplugin_pygments', # https://github.com/chrisglass/cmsplugin-pygments

    'reversion', # https://github.com/etianen/django-reversion
    'reversion_compare', # https://github.com/jedie/django-reversion-compare
    'compressor', # https://github.com/django-compressor/django-compressor
    'django_extensions', # https://github.com/django-extensions/django-extensions

    # djangocms-blog
    'filer',
    'easy_thumbnails',
    'cmsplugin_filer_image',
    'parler',
    'taggit',
    'taggit_autosuggest',
    'django_select2',
    'meta',
    'meta_mixin',
    'admin_enhancer',
    'djangocms_blog',

    # own apps:
    'django_info_panel',
    'pylucid',
)

CMS_TEMPLATES = (
    ('fullwidth.html', 'Full-width template'),
    ('sidebar_left.html', 'Sidebar left template'),
    ('homepage.html', 'Homepage template'),
)

CMS_PERMISSION = True

# http://django-cms.readthedocs.org/en/support-3.0.x/reference/configuration.html#cms-placeholder-conf
CMS_PLACEHOLDER_CONF = {
    'content': {
        'name' : _('Content'),

        # list of plugins that can be added to this placeholder. If not supplied, all plugins can be selected:
        #'plugins': ['TextPlugin', 'LinkPlugin'],

        # list of default plugins which will be automagically added when the placeholder will be created:
        'default_plugins':[
            {
                'plugin_type':'TextPlugin',
                'values':{'body':'<p>(There is no content, yet.)</p>'},
            },
        ]
    },
    'post_content': {
        'name' : _('Blog Content'),
        # list of default plugins which will be automagically added when the placeholder will be created:
        'default_plugins':[
            {
                'plugin_type':'TextPlugin',
                'values':{'body':'<p>(There is no content, yet.)</p>'},
            },
        ]
    },
}



MIGRATION_MODULES = {
    'cms': 'cms.migrations_django',
    'menus': 'menus.migrations_django',
    'djangocms_text_ckeditor': 'djangocms_text_ckeditor.migrations_django',
    # 'djangocms_column': 'djangocms_column.migrations_django',
    # 'djangocms_flash': 'djangocms_flash.migrations_django',
    # 'djangocms_googlemap': 'djangocms_googlemap.migrations_django',
    # 'djangocms_inherit': 'djangocms_inherit.migrations_django',
    # 'djangocms_style': 'djangocms_style.migrations_django',
    'djangocms_file': 'djangocms_file.migrations_django',
    'djangocms_link': 'djangocms_link.migrations_django',
    'djangocms_picture': 'djangocms_picture.migrations_django',
    # 'djangocms_teaser': 'djangocms_teaser.migrations_django',
    'djangocms_video': 'djangocms_video.migrations_django',

    # for djangocms-blog:
    'filer': 'filer.migrations_django',
    'cmsplugin_filer_image': 'cmsplugin_filer_image.migrations_django',
}


# django-reversion-compare settings:
ADD_REVERSION_ADMIN=True # Add the reversion modes to admin interface


# django-debug-toolbar settings:
DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',

    'django_info_panel.panels.database.DatabaseInfo',
    'django_info_panel.panels.urlpatterns.UrlPatternsInfo',
    'django_info_panel.panels.template.TemplateInfo',
]


# https://github.com/nephila/djangocms-blog#quick-hint
SOUTH_MIGRATION_MODULES = {
    'easy_thumbnails': 'easy_thumbnails.south_migrations',
    'taggit': 'taggit.south_migrations',
}


# http://django-filer.readthedocs.org/en/latest/installation.html#configuration
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)


# https://github.com/nephila/django-meta#configuration
META_SITE_PROTOCOL = "http" # This should be set to either 'http' or 'https'
META_USE_SITES = True # use Django's sites contrib app

#----------------------------------------------------------
# language setup
# note there are three places for language related settings:
#  * django
#  * djangocms
#  * django-parler (for djangocms-blog)
#
# see also: https://docs.djangoproject.com/en/1.7/topics/i18n/

# https://docs.djangoproject.com/en/1.7/ref/settings/#languages
LANGUAGES = (
    ('en', _('English')),
    ('de', _('German')),
)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# languages available in django CMS:
# http://docs.django-cms.org/en/stable/reference/configuration.html#std:setting-CMS_LANGUAGES
CMS_LANGUAGES = {
    'default': { # all SITE_ID's
        'fallbacks': ['en', 'de'],
        'redirect_on_fallback': True,
        'public': True,
        'hide_untranslated': False,
    },
    # 1: [ # SITE_ID == 1
    #     {
    #         'redirect_on_fallback': True,
    #         'public': True,
    #         'hide_untranslated': False,
    #         'code': 'en',
    #         'name': _('English'),
    #     },
    #     {
    #         'redirect_on_fallback': True,
    #         'public': True,
    #         'hide_untranslated': False,
    #         'code': 'de',
    #         'name': _('Deutsch'),
    #     },
    # ],
}

# http://django-parler.readthedocs.org/en/latest/quickstart.html#configuration
PARLER_DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE
PARLER_LANGUAGES = {
    None: (
        {'code': 'en',},
        {'code': 'de',},
    ),
    # 1: ( # SITE_ID == 1
    #     {'code': 'en',},
    #     {'code': 'de',},
    # ),
    # 2: ( # SITE_ID == 2
    #     {'code': 'en',},
    #     {'code': 'de',},
    # ),
    'default': {
        'fallback': PARLER_DEFAULT_LANGUAGE_CODE,
        'hide_untranslated': False,   # the default; let .active_translations() return fallbacks too.
    }
}