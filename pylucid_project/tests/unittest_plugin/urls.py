# coding: utf-8

from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$',              views.view_root,    name='UnittestPlugin-view_root'),
    url(r'^view_a/$',       views.view_a,       name='UnittestPlugin-view_a'),
    url(r'^view_b/(.*?)$',  views.view_b,       name='UnittestPlugin-view_b'),
    url(r'^view_c/$',       views.view_c,       name='UnittestPlugin-view_c'),
)
