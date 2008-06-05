# -*- coding: utf-8 -*-
"""
    PyLucid utils
    ~~~~~~~~~~~~~

    Some tiny shared functions.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import warnings

from django.conf import settings
from django.core.cache import cache

from PyLucid.system.page_msg import PageMessages



def delete_page_cache():
    """
    Delete all pages in the cache.
    Needed, if:
        - A template has been edited
        - The menu changes (edit the page name, position, parent link)
    TODO: move this function from models.py into a other nice place...
    """
    from PyLucid.models import Page
    for items in Page.objects.values('shortcut').iterator():
        shortcut = items["shortcut"]
        cache_key = settings.PAGE_CACHE_PREFIX + shortcut
        cache.delete(cache_key)

#______________________________________________________________________________

def redirect_warnings(out_obj):
    """
    Redirect every "warning" messages into the out_obj.
    """
#    old_showwarning = warnings.showwarning
    def showwarning(message, category, filename, lineno):
        msg = unicode(message)
        if settings.DEBUG:
            filename = u"..." + filename[-30:]
            msg += u" (%s - line %s)" % (filename, lineno)
        out_obj.write(msg)

    warnings.showwarning = showwarning


def setup_request(request):
    """
    Setup the request object

    -add the attribute "debug" and "page_msg" to the request object.
    -Redirect every "warning" messages into the page_msg

    Used in:
        - PyLucid.middlewares.common
        - PyLucid.install.BaseInstall
    """
    # Setup request.debug
    if settings.DEBUG or \
                request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
        request.debug = True
    else:
        request.debug = False

    # Add page_msg
    request.page_msg = PageMessages(request)

    # Redirect every "warning" messages into the page_msg:
    redirect_warnings(request.page_msg)


def get_uri_base():
    """
    This function should be only used, if the request object is not available.
    e.g. in the model class to build a absolute uri.

    note: it returns the domain without a trailed slash!

    The better way is to use request.build_absolute_uri():
    http://www.djangoproject.com/documentation/request_response/#methods
    """
    if os.environ.get("HTTPS") == "on":
        protocol = "https"
    else:
        protocol = "http"

    # PyLucid doen't use the site framework:
    # domain = Site.objects.get_current().domain
    domain = os.environ.get("SERVER_NAME")
    if not domain:
        domain = os.environ.get("HTTP_HOST")
    if not domain:
        # Can't build the complete uri without the domain ;(
        # e.g. running the django development server
        return ""

    return "%s://%s" % (protocol, domain)
