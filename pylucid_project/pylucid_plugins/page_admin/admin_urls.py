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


urlpatterns = patterns('page_admin.admin_views',
    url(r'^new_content_page/$', "new_content_page", name='PageAdmin-new_content_page'),
    url(r'^new_plugin_page/$', "new_plugin_page", name='PageAdmin-new_plugin_page'),
    url(r'^edit_page/(?P<pagetree_id>\d+?)/$', "edit_page", name='PageAdmin-edit_page'),
    url(r'^translate/(?P<pagemeta_id>\d+?)/$', "translate", name='PageAdmin-translate'),
    url(r'^tag_list/$', "tag_list", name='PageAdmin-tag_list'),
)
