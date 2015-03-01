import tempfile
from pylucid_installer.page_instance_template.example_project.settings import *

DEBUG = True
TEMPLATE_DEBUG = True

UNITTEST_TEMP_PATH = tempfile.mkdtemp(prefix="pylucid_design_demo_")
print("Use temp dir: %r" % UNITTEST_TEMP_PATH)

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove("example_project")
INSTALLED_APPS = tuple(INSTALLED_APPS)

INSTALLED_APPS += (
    "pylucid_design_demo",
    'debug_toolbar', # django-debug-toolbar - https://github.com/django-debug-toolbar/django-debug-toolbar

    # Add all models to django admin:
    'pylucid_debug', # Must be the last App!
)

ROOT_URLCONF = 'pylucid.base_urls'

WSGI_APPLICATION = 'pylucid_design_demo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(UNITTEST_TEMP_PATH, 'cmsplugin_markup_unittest_database'),
    }
}
DEBUG_TOOLBAR_CONFIG = {
    # For local debugging: print information if IP address not in INTERNAL_IPS
    "SHOW_TOOLBAR_CALLBACK":"pylucid_debug.debug_toolbar_helper.show_toolbar",
}

# Disable cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
#

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE_CLASSES