# coding: utf-8

from django.conf.urls.defaults import patterns, url

from auth.views import login, logout 

urlpatterns = patterns('',
    url(r'^login/$', login, name='PluginAuth-login'),
    url(r'^logout/$', logout, name='PluginAuth-logout'),
)
