#!/usr/bin/env python
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

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os

from django.conf import settings

def setup_debug(request):
    """
    add the attribute "debug" to the request object.
    """
    if settings.DEBUG and \
                request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
        request.debug = True
    else:
        request.debug = False

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