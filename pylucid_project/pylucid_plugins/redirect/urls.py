# coding: utf-8

from django.conf.urls.defaults import patterns, url

from redirect import views

urlpatterns = patterns('',
    url(r'^(?P<rest_url>.*?)$', views.redirect, name='PluginRedirect-redirect'),
    # FIXME: Don't known why PluginPageManager().get_app_choices() does only add this plugin
    # if we add this url pattern:
    url(r'^', views.redirect, name='PluginRedirect-redirect-index'),
)


