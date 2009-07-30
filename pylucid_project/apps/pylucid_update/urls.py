# -*- coding: utf-8 -*-

"""
    urls for update section
"""

from django.conf.urls.defaults import patterns, url

from pylucid_project.apps.pylucid_update import views
from pylucid.decorators import superuser_only

urlpatterns = patterns('',
    url(r'^$', views.menu, name='PyLucidUpdate-menu'),
    url(r'^update08/$', views.update08, name='PyLucidUpdate-update08'),
    url(r'^update08templates/$', views.update08templates, name='PyLucidUpdate-update08templates'),
    url(r'^update08styles/$', views.update08styles, name='PyLucidUpdate-update08styles'),
    url(r'^update08plugins/$', views.update08plugins, name='PyLucidUpdate-update08plugins'),
)
