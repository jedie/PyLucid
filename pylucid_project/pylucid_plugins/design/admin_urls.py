# coding: utf-8

"""
    PyLucid admin views url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls import patterns, url

from design import admin_views

urlpatterns = patterns('',
    url(r'^switch/$', admin_views.switch, name='Design-switch'),
    url(r'^clone/$', admin_views.clone, name='Design-clone'),
    url(r'^rename_colors/(?P<colorscheme_id>\d+)?/$', admin_views.rename_colors, name='Design-rename_colors'),
)

