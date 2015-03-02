import tempfile
from pylucid_installer.page_instance_template.example_project.settings import *

DEBUG = True
TEMPLATE_DEBUG = True

UNITTEST_TEMP_PATH = tempfile.mkdtemp(prefix="pylucid_design_demo_")
print("Use temp dir: %r" % UNITTEST_TEMP_PATH)

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove("example_project")
INSTALLED_APPS.append("pylucid_design_demo")
INSTALLED_APPS = tuple(INSTALLED_APPS)

ROOT_URLCONF = 'pylucid.base_urls'

WSGI_APPLICATION = 'pylucid_design_demo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(UNITTEST_TEMP_PATH, 'cmsplugin_markup_unittest_database'),
    }
}