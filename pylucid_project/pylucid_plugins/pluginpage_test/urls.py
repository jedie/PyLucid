# coding: utf-8

from django.conf.urls.defaults import patterns, url

from pluginpage_test import views

urlpatterns = patterns('',
    url(r'^/$', views.view_root,name='PluginTest-view_root'),
    url(r'^view_a/$', views.view_a, name='PluginTest-view_a'),
    url(r'^view_b/$', views.view_b, name='PluginTest-view_b'),
    url(r'^view_c/$', views.view_c, name='PluginTest-view_c'),
)
