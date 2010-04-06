# coding: utf-8

from django.conf.urls.defaults import patterns, url

from update_journal import views

urlpatterns = patterns('',
    url(r'^(?P<filename>.+?)$', views.feed, name='UpdateJournal-feed'),
    url(r'^', views.select_feed, name='UpdateJournal-select_feed'),
)
