# coding: utf-8

from django.conf.urls.defaults import patterns, url

from blog.views import summary, tag_view, detail_view, feed, select_feed

urlpatterns = patterns('',
    url(r'^tags/(?P<tags>.+?)/$', tag_view, name='Blog-tag_view'),
    url(r'^(?P<id>\d+?)/(?P<title>.*)/$', detail_view, name='Blog-detail_view'),

    url(r'^feed/(?P<tags>.+)/(?P<filename>.+?)$', feed, name='Blog-tag_feed'),
    url(r'^feed/(?P<filename>.+?)$', feed, name='Blog-feed'),
    url(r'^feed/', select_feed, name='Blog-select_feed'),

    url(r'^', summary, name='Blog-summary'),
)
