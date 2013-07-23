# coding: utf-8


from django.conf.urls import patterns, url

from pylucid_project.pylucid_plugins.auth import views


urlpatterns = patterns('',
    url(r'^', views.login_honeypot, name='Auth-login_honeypot'),
)
