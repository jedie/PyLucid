# coding: utf-8

from django.conf.urls.defaults import patterns, url

from blog.views import summary, tag_view

urlpatterns = patterns('',
    url(r'^$', summary, name='Blog-summary'),
    url(r'^tags/(?P<tag>.*?)$', tag_view, name='Blog-tag_view'),
)
