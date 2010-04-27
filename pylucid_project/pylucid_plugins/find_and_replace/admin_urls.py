# coding: utf-8

"""
    PyLucid admin url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls.defaults import patterns, url

from find_and_replace import admin_views

urlpatterns = patterns('',
    url(r'^find_and_replace/$', admin_views.find_and_replace, name='FindAndReplace-find_and_replace'),
)

