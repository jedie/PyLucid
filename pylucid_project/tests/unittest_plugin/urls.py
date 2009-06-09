# coding: utf-8

from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(
        r'^$',
        views.view_root, name='UnittestPlugin-view_root'
    ),
    url(
        r'^test_HttpResponse/$',
        views.test_HttpResponse, name='UnittestPlugin-test_HttpResponse'
    ),
    url(
        r'^test_plugin_template/$',
        views.test_plugin_template, name='UnittestPlugin-test_plugin_template'
    ),
    url(
        r'^args_test/(?P<arg1>.*?)/(?P<arg2>.*?)/$',
        views.test_url_args,  name='UnittestPlugin-test_url_args'
    ),
    url(
        r'^test_return_none/$',
        views.test_return_none, name='UnittestPlugin-test_return_none'
    ),
    url(
        r'^test_url_reverse/(?P<url_name>.*?)/$',
        views.test_url_reverse,  name='UnittestPlugin-test_url_reverse'
    ),    
    url(
        r'^test_PyLucid_api/$',
        views.test_PyLucid_api, name='UnittestPlugin-test_PyLucid_api'
    ),
    url(
        r'^test_BreadcrumbPlugin/$',
        views.test_BreadcrumbPlugin, name='UnittestPlugin-test_BreadcrumbPlugin'
    ),
    
    url(
        r'^test_add_headfiles/$',
        views.test_add_headfiles, name='UnittestPlugin-test_add_headfiles'
    ),

)
