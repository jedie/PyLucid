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

from tools import admin_views

urlpatterns = patterns('',
    url(r'^highlight_code/$', admin_views.highlight_code, name='Tools-highlight_code'),
    url(r'^cleanup_log/$', admin_views.cleanup_log, name='Tools-cleanup_log'),
    url(r'^cleanup_session/$', admin_views.cleanup_session, name='Tools-cleanup_session'),
    url(r'^overwrite_template/$', admin_views.overwrite_template, name='Tools-overwrite_template'),
)

