# coding: utf-8

"""
    Django settings for example_project project
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Quick-start development settings - unsuitable for production:
        https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

    For more information on this file, see:
        https://docs.djangoproject.com/en/1.11/topics/settings/

    For the full list of settings and their values, see:
        https://docs.djangoproject.com/en/1.11/ref/settings/
"""
from pathlib import Path

from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-tools
from django_tools.settings_utils import InternalIps

# PyLucid
from pylucid.base_settings import *

DOC_ROOT = "/path/to/page_instance/" # Point this to web server root directory

STATIC_ROOT = str(Path(DOC_ROOT, "static"))
MEDIA_ROOT = str(Path(DOC_ROOT, "media"))


PROJECT_DIR = Path(__file__).resolve().parent # Filesystem path to this instance

# Place for own templates:
TEMPLATES[0]["DIRS"] = [str(Path(PROJECT_DIR, "templates/"))]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "CHANGE ME!!!"


ROOT_URLCONF = "example_project.urls"

WSGI_APPLICATION = "example_project.wsgi.application"


# INSTALLED_APPS += (
#     #"example_project",
#
#     # Activate if old PyLucid migration was executed
#     # "pylucid_todo",
# )

# # Your own djangocms-widgets templates:
# WIDGET_TEMPLATES += (
#     #("foo/bar.html", "A foo bar example"),
# )

#____________________________________________________________________
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "HOST": "localhost",
        "PORT": "",
        "USER": "",
        "PASSWORD": "",
        "NAME": str(Path(PROJECT_DIR, "example_project.db")),
        "ATOMIC_REQUESTS": True,
    },
}

#____________________________________________________________________
# Please change email-/SMTP-Settings:

# https://docs.djangoproject.com/en/1.11/ref/settings/#email-host
EMAIL_HOST = "localhost"
EMAIL_HOST_USER = "root@%s" % EMAIL_HOST
EMAIL_HOST_PASSWORD = ""

# https://docs.djangoproject.com/en/1.11/ref/settings/#default-from-email
# email address to use for various automated correspondence from the site manager(s). Except error mails:
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# https://docs.djangoproject.com/en/1.11/ref/settings/#server-email
# Email address that error messages come from:
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# https://docs.djangoproject.com/en/1.11/ref/settings/#managers
# A tuple that lists people who get broken link notifications when BrokenLinkEmailsMiddleware is enabled:
#MANAGERS = (("John", "john@example.com"), ("Mary", "mary@example.com"))

# https://docs.djangoproject.com/en/1.11/ref/settings/#admins
# A tuple that lists people who get code error notifications:
#ADMINS = MANAGERS




# https://docs.djangoproject.com/en/1.11/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "*", # Allow any domain/subdomain
    # "www.example.tld",  # Allow domain
    # ".example.tld",  # Allow domain and subdomains
    # ".example.tld.",  # Also allow FQDN and subdomains
]

#____________________________________________________________________
# DEBUG

# *** SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# https://github.com/jedie/django-tools#internalips---unix-shell-style-wildcards-in-internal_ips
INTERNAL_IPS = InternalIps(["127.0.0.1", "::1", "192.168.*.*", "10.0.*.*"])


if DEBUG:
    # Turns on all warnings
    warnings.simplefilter("always")


#____________________________________________________________________
# extra DEBUG
#
# if DEBUG:
#     # Disable cache, for debugging:
#     CACHES["default"]= {
#         "BACKEND": "django.core.cache.backends.dummy.DummyCache",
#     }
#
#     INSTALLED_APPS += (
#         "debug_toolbar", # https://github.com/django-debug-toolbar/django-debug-toolbar
#         "django_info_panel", # https://github.com/jedie/django-debug-toolbar-django-info
#
#         # Add all models to django admin:
#         "pylucid_debug", # Must be the last App!
#     )
#     MIDDLEWARE_CLASSES = (
#         "debug_toolbar.middleware.DebugToolbarMiddleware",
#     ) + MIDDLEWARE_CLASSES
