# -*- coding: utf-8 -*-

"""
    Generate dynamicly urls based on the database tree
"""

from django.conf.urls.defaults import patterns, url

from pylucid_project.apps.pylucid_update.views import menu, update08

urlpatterns = patterns('',
    url(r'/$',          menu,     name='PyLucidUpdate-menu'),
    url(r'/update08/',  update08, name='PyLucidUpdate-update08'),
)
