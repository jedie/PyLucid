# -*- coding: utf-8 -*-

"""
    urls for update section
"""

from django.conf.urls.defaults import patterns, url

from pylucid_project.apps.pylucid_update import views
from pylucid_project.apps.pylucid.decorators import superuser_only

urlpatterns = patterns('',
    url(r'^$', views.menu, name='PyLucidUpdate-menu'),
    url(r'^wipe_site/$', views.wipe_site, name='PyLucidUpdate-wipe_site'),
    url(r'^replace08URLs/$', views.replace08URLs, name='PyLucidUpdate-replace08URLs'),
    url(r'^update08migrate_stj/$', views.update08migrate_stj, name='PyLucidUpdate-update08migrate_stj'),
    url(r'^update08migrate_pages/$', views.update08migrate_pages, name='PyLucidUpdate-update08migrate_pages'),
    url(r'^update08pages/$', views.update08pages, name='PyLucidUpdate-update08pages'),
    url(r'^update08pagesRedirect/$', views.update08pagesRedirect, name='PyLucidUpdate-update08pagesRedirect'),
    url(r'^update08templates/$', views.update08templates, name='PyLucidUpdate-update08templates'),
    url(r'^update08styles/$', views.update08styles, name='PyLucidUpdate-update08styles'),
    url(r'^update08plugins/$', views.update08plugins, name='PyLucidUpdate-update08plugins'),
)
