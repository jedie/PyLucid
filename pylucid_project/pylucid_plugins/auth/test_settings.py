
from pylucid_project.settings import *

DEBUG = True

# Database connection info.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
