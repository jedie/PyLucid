# coding: utf-8

"""
    PyLucid admin url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls.defaults import patterns, url

# XXX: why doesn't this work: from system.admin_views import base_check, timezone
from admin_views import base_check, timezone

urlpatterns = patterns('',
    url(r'^base_check/$', base_check, name='System-base_check'),
    url(r'^timezone/$', timezone, name='System-timezone'),
)

