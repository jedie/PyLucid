# coding: utf-8

"""
    PyLucid admin url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns, url

from pylucid_project.apps.pylucid.decorators import superuser_only
from pylucid_project.apps.pylucid.markup.views import markup_preview

from blog import admin_views


urlpatterns = patterns('',
    url(r'^new_blog_entry/$', admin_views.new_blog_entry, name='Blog-new_blog_entry'),
    url(r'^new_blog_entry/preview/$', markup_preview, name='Blog-markup_preview'),

    url(r'^translate/(?P<id>\d+?)/$', admin_views.translate_blog_entry, name='Blog-translate'),
    url(r'^translate/\d+?/preview/$', markup_preview, name='Blog-translate_markup_preview'),
)

