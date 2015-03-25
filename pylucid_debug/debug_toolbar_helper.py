# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings

from debug_toolbar.middleware import show_toolbar as origin_show_toolbar


def show_toolbar(request):
    """
    The same as origin, but print information if REMOTE_ADDR: not in settings.INTERNAL_IPS
    """
    ip = request.META.get('REMOTE_ADDR', None)
    if ip not in settings.INTERNAL_IPS:
        print("REMOTE_ADDR: %r not in settings.INTERNAL_IPS: %r !" % (ip,settings.INTERNAL_IPS))

    return origin_show_toolbar(request)