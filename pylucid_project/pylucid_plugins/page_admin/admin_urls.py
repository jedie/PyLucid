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

from page_admin import admin_views

urlpatterns = patterns('',
    url(r'^new_content_page$', admin_views.new_content_page, name='PageAdmin-new_content_page'),
    url(r'^new_plugin_page$', admin_views.new_plugin_page, name='PageAdmin-new_plugin_page'),
    #url(r'^view2$', admin_views.test2, name='extrahead-view2'),
)
#menu_info = (
#    {"menu section": _("Page Admin"), "name":False}
#)

