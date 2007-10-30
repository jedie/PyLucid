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