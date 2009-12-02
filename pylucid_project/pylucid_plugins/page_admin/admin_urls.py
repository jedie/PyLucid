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

from pylucid_project.pylucid_plugins.page_admin import admin_views

urlpatterns = patterns('',
    url(r'^new_content_page/$', admin_views.new_content_page, name='PageAdmin-new_content_page'),
    url(r'^new_plugin_page/$', admin_views.new_plugin_page, name='PageAdmin-new_plugin_page'),
    url(r'^edit_page/(?P<pagetree_id>\d+?)/$', admin_views.edit_page, name='PageAdmin-edit_page'),
    url(r'^page_order/(?P<pagetree_id>\d+?)/$', admin_views.page_order, name='PageAdmin-page_order'),
    url(r'^translate/(?P<pagemeta_id>\d+?)/$', admin_views.translate, name='PageAdmin-translate'),
    url(r'^tag_list/$', admin_views.tag_list, name='PageAdmin-tag_list'),
)
