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

from pylucid_project.pylucid_plugins.tools.admin_views import highlight_code

urlpatterns = patterns('',
    url(r'^highlight_code/$', highlight_code, name='Tools-highlight_code'),
)

