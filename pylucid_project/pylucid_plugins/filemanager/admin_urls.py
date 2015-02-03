# coding: utf-8

"""
    PyLucid admin url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls import patterns, url

from pylucid_project.pylucid_plugins.filemanager import admin_views

urlpatterns = patterns('',
    url(r'^filemanager/$', admin_views.index, name='Filemanager-index'),
    url(r'^filemanager/(?P<no>\d)/(?P<rest_url>.*?)$', admin_views.filemanager, name='Filemanager-filemanager'),
)
