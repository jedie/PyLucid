 # -*- coding: utf-8 -*-

"""
    PyLucid shared middleware utils
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.utils.encoding import smart_str

MAX_FILEPATH_LEN = 50
FILEPATH_SPLIT = "src/pylucid" # try to cut the filepath or MAX_FILEPATH_LEN used


def replace_content(response, old, new):
    """
    -replace 'old' with 'new' in the response content.
    -returns the response object
    """
    old = smart_str(old, encoding=settings.DEFAULT_CHARSET)
    new = smart_str(new, encoding=settings.DEFAULT_CHARSET)

    # replace
    try:
        response.content = response.content.replace(old, new)
    except UnicodeError, err:
        pass

    return response


def cut_filename(filename):
    """ used in page_msg and pagestats """
    if FILEPATH_SPLIT in filename:
        return "...%s" % filename.split(FILEPATH_SPLIT)[1]
    if len(filename) >= MAX_FILEPATH_LEN:
        filename = "...%s" % filename[-MAX_FILEPATH_LEN:]
    return filename
