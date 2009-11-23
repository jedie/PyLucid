# coding: utf-8

from django.conf.urls.defaults import patterns, url

from lexicon.views import summary, detail_view

urlpatterns = patterns('',
    url(r'^/detail/(?P<term>.*?)/$', detail_view, name='Lexicon-detail_view'),
    url(r'^', summary, name='Lexicon-summary'),
)
