# coding: utf-8

"""
    PyLucid admin views url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls import patterns, url

from update_env import admin_views

urlpatterns = patterns('',
    url(r'^status/$', admin_views.status, name='Update-status'),
    url(r'^update/(?P<src_name>.*?)/$', admin_views.update, name='Update-update'),
)

