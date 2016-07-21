# coding: utf-8

"""
    PyLucid base settings
    ~~~~~~~~~~~~~~~~~~~~~

    see also:
    https://github.com/django/django/blob/master/django/conf/global_settings.py
    https://docs.djangoproject.com/en/1.8/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy as _
# _ = lambda s: s


ALLOWED_HOSTS = []

TIME_ZONE = 'America/Chicago'
LANGUAGES = (
    ('en', _('English')),
)
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True

# If you set this to True, Django will use timezone-aware datetimes:
USE_TZ = False

DEBUG = False

INTERNAL_IPS = (
    '127.0.0.1',
    '::1',
)


CACHES = {
    'default': {
        # https://docs.djangoproject.com/en/1.8/topics/cache/#database-caching
        # manage.py createcachetable
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    },
}

SITE_ID = 1


MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',

    'cms.middleware.utils.ApphookReloadMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
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
            'cms.context_processors.cms_settings',
            'pylucid.context_processors.pylucid',
        ],
    },
},]



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_FINDERS = (
    "compressor.finders.CompressorFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
)

INSTALLED_APPS = (
    'djangocms_admin_style', # must be inserted before django.contrib.admin

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',

    'pylucid',

    'cms',

    'djangocms_text_ckeditor',
    'menus',
    'sekizai',
    'treebeard',

    # https://github.com/stefanfoulis/django-filer
    'filer',
    'easy_thumbnails',
    # https://github.com/stefanfoulis/cmsplugin-filer
    'cmsplugin_filer_file',
    'cmsplugin_filer_folder',
    'cmsplugin_filer_link',
    'cmsplugin_filer_image',
    'cmsplugin_filer_teaser',
    'cmsplugin_filer_utils',
    'cmsplugin_filer_video',

    'djangocms_htmlsitemap', # https://github.com/kapt-labs/djangocms-htmlsitemap
    'cmsplugin_pygments', # https://github.com/chrisglass/cmsplugin-pygments
    'cmsplugin_markup', # https://github.com/mitar/cmsplugin-markup

    'reversion', # https://github.com/etianen/django-reversion
    'reversion_compare', # https://github.com/jedie/django-reversion-compare
    'compressor', # https://github.com/django-compressor/django-compressor

    # djangocms-blog
    'parler',
    'taggit',
    'taggit_autosuggest',
    'meta',
    'meta_mixin',
    'aldryn_apphooks_config',
    'djangocms_blog',

    'djangocms_widgets',
    'djangocms_widgets_socialshareprivacy',

    # Installed only in developer installation:
    #'django_extensions', # https://github.com/django-extensions/django-extensions
)

# djangocms_widgets
WIDGET_TEMPLATES = (
    ('socialshareprivacy.html', 'SocialSharePrivacy'), # djangocms_widgets_socialshareprivacy
)

CMS_TEMPLATES = (
    ('pylucid/bootstrap/split_tree_menu_left.html', 'Split tree menu left'),
    ('pylucid/bootstrap/fullwidth.html', 'Top menu - full width'),
    ('pylucid/bootstrap/sidebar_left.html', 'Top menu with sidebar left'),
    ('pylucid/bootstrap/homepage.html', 'Homepage template'),
    ('pylucid/bootstrap/tree_menu_left.html', 'Tree menu left'),
    ('pylucid/bootstrap/tree_menu_right.html', 'Tree menu right'),
    ('pylucid/simple.html', 'Simple'),
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
    'djangocms_text_ckeditor': 'djangocms_text_ckeditor.migrations',
    'cmsplugin_markup': 'cmsplugin_markup.migrations_django',
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

    # https://github.com/jedie/django-debug-toolbar-django-info
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

# DEBUG_TOOLBAR_CONFIG = {
#     # For local debugging: print information if IP address not in INTERNAL_IPS
#     "SHOW_TOOLBAR_CALLBACK":"pylucid_debug.debug_toolbar_helper.show_toolbar",
# }



LOGIN_REDIRECT_URL="/"
LOGIN_URL="/admin/login/"
LOGOUT_URL="/admin/logout/"