# -*- coding: utf-8 -*-

"""
    PyLucid path manager
    ~~~~~~~~~~~~~~~~~~~~

    Tools around handling path in PyLucid.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

import os

from django.conf import settings

#______________________________________________________________________________
# Build a list and a dict from the basepaths
# The dict key is a string, not a integer. (GET/POST Data always returned
# numbers as strings)

BASE_PATHS = [
    (str(no), unicode(path)) for no, path in enumerate(
                                                settings.FILEMANAGER_BASEPATHS)
]
BASE_PATHS_DICT = dict(BASE_PATHS)

#______________________________________________________________________________
_MEDIA_DIR_CACHE = None
def get_media_dirs():
    global _MEDIA_DIR_CACHE
    if _MEDIA_DIR_CACHE == None:
        _MEDIA_DIR_CACHE = [root for root, _, _ in os.walk(settings.MEDIA_ROOT)]

    return _MEDIA_DIR_CACHE

