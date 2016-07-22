from pylucid_installer.page_instance_template.example_project.settings import *
import pylucid_design_demo

DEBUG = True
TEMPLATE_DEBUG = True

TEST_USERNAME="test"
TEST_USERPASS="12345678"

from django_tools.settings_utils import InternalIps

INTERNAL_IPS = InternalIps(["127.0.0.1", "::1", "192.168.*.*", "10.0.*.*"])

UNITTEST_TEMP_PATH = os.environ["UNITTEST_TEMP_PATH"]
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
ROOT_URLCONF = 'pylucid_design_demo.urls'
WSGI_APPLICATION = 'pylucid_design_demo.wsgi.application'

TEMPLATES[0]["DIRS"].insert(0,
    os.path.join(os.path.dirname(pylucid_design_demo.__file__), 'templates')
)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(UNITTEST_TEMP_PATH, 'cmsplugin_markup_unittest_database'),
        # 'NAME': ":memory:", # in memory DB seems not to work here :(
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
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}