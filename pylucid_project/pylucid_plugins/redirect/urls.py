# coding: utf-8

from django.conf.urls.defaults import patterns, url

from redirect import views

urlpatterns = patterns('',
    url(r'^(?P<rest_url>.*?)$', views.redirect, name='PluginRedirect-redirect'),
)


