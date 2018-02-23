
"""
    page instance setting example
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Here should be only set stuff depend on page instance (e.g.: project path)
"""

from pylucid.base_settings import *

# For build paths inside the project:
BASE_DIR = Path(__file__).resolve().parent


TEMPLATES[0]["DIRS"] = [str(Path(BASE_DIR, "templates/"))]

STATIC_ROOT = str(Path(BASE_DIR, 'static'))
MEDIA_ROOT = str(Path(BASE_DIR, 'media'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(Path(BASE_DIR, '..', 'test_project_db.sqlite3').resolve()),
    }
}
