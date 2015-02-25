
import os
import tempfile

from pylucid_installer.page_instance_template.example_project.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(tempfile.tempdir or ".", 'pylucid_unittest_database'),
    }
}