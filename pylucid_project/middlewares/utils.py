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
