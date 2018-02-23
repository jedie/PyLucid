
"""
    page instance setting example
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Here should be only set stuff depend on page instance (e.g.: project path)
"""

from pylucid.base_settings import *

# For build paths inside the project:
BASE_DIR = Path(__file__).resolve().parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'Only for the tests ;)'


DEBUG = True


TEMPLATES[0]["DIRS"] = [str(Path(BASE_DIR, "templates/"))]


STATIC_ROOT = str(Path(BASE_DIR, 'static'))
MEDIA_ROOT = str(Path(BASE_DIR, 'media'))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(Path(BASE_DIR, '..', 'test_project_db.sqlite3').resolve()),
    }
}
