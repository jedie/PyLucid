# coding: utf-8

from django.conf.urls.defaults import patterns, url

from pylucid_comments.views import comment_form

urlpatterns = patterns('',
    url(r'^comment_form/', comment_form, name='PageComments-comment_form'),
)
