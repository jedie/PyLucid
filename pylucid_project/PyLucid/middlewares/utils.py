 # -*- coding: utf-8 -*-

"""
    PyLucid shared middleware utils
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

def is_html(response):
    """
    returns a Bool if the response is a html page or not.
    """
    if not "html" in response._headers["content-type"][1]:
        # Isn't a HTML page
        return False
    else:
        # Is a HTML Page
        return True

def replace_content(response, old, new):
    """
    -replace 'old' with 'new' in the response content.
    -returns the response object
    """
    content = response.content
    if not isinstance(content, unicode):
        # FIXME: In my shared webhosting environment is response.content a
        # string and not unicode. Why?
        from django.utils.encoding import force_unicode
        try:
            content = force_unicode(content)
        except:
            return response

    # replace
    new_content = content.replace(old, new)
    response.content = new_content

    return response
