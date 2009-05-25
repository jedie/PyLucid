# coding: utf-8

from django.conf.urls.defaults import patterns, url

from auth.views import authenticate

urlpatterns = patterns('',
    url(r'^$', authenticate, name='PluginAuth'),
)
