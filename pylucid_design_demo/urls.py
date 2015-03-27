# coding: utf-8

"""
    PyLucid DesignSwitch Plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls import patterns, url

from pylucid.base_urls import urlpatterns

from . import views

urlpatterns = patterns('',
    url(r'^__switch_template__/page(?P<page_id>\d+)/(?P<template>.+)$', views.switch_template, name="switch_template"),
) + urlpatterns
