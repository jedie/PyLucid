# coding: utf-8

"""
    local settings used in unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

print "Using %s, ok." % __file__

import os
import tempfile


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ":memory:",
    }
}


SECRET_KEY = "i'm not secret"


_tempdir = tempfile.gettempdir()

MEDIA_ROOT = os.path.join(_tempdir, "pylucid_unittest_media")
if not os.path.isdir(MEDIA_ROOT):
    os.mkdir(MEDIA_ROOT)
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(_tempdir, "pylucid_unittest_static")
if not os.path.isdir(STATIC_ROOT):
    os.mkdir(STATIC_ROOT)
STATIC_URL = '/static/'

print "use MEDIA_ROOT: %s" % MEDIA_ROOT
print "use STATIC_ROOT: %s" % STATIC_ROOT