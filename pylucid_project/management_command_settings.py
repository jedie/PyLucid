# coding: utf-8

"""
    local settings used in management commands
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    e.g. for create page instance
    
    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

print "Using %s, ok." % __file__

SECRET_KEY = "i'm not secret and only used for management commands!"

MEDIA_ROOT = ""
MEDIA_URL = ""

STATIC_ROOT = ""
STATIC_URL = ""

# django-compressor - ImproperlyConfigured: URL settings (e.g. COMPRESS_URL) must have a trailing slash
COMPRESS_URL = "/fake/"
