# coding: utf-8

from django.conf.urls import patterns, url

from gallery import views

urlpatterns = patterns('',
    url(r'^(?P<rest_url>.*?)$', views.gallery, name='PluginGallery'),
)


