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

from django.conf.urls.defaults import patterns, url

from admin_views.bulk_editor import bulk_editor
from admin_views.edit_page import edit_page
from admin_views.convert_markup import convert_markup
from admin_views.new_content_page import new_content_page
from admin_views.new_plugin_page import new_plugin_page
from admin_views.page_order import page_order
from admin_views.tag_list import tag_list
from admin_views.page_list import page_list
from admin_views.markup_help import markup_help
from admin_views.translate_page import translate_page


urlpatterns = patterns('',
    url(r'^new_content_page/$', new_content_page, name='PageAdmin-new_content_page'),
    url(r'^new_plugin_page/$', new_plugin_page, name='PageAdmin-new_plugin_page'),
    url(r'^convert_markup/(?P<pagecontent_id>\d+?)/$', convert_markup, name='PageAdmin-convert_markup'),
    url(r'^edit_page/(?P<pagetree_id>\d+?)/$', edit_page, name='PageAdmin-edit_page'),
    url(r'^page_order/(?P<pagetree_id>\d+?)/$', page_order, name='PageAdmin-page_order'),
    url(r'^translate/(?P<pagemeta_id>\d+?)/$', translate_page, name='PageAdmin-translate'),
    url(r'^tag_list/$', tag_list, name='PageAdmin-tag_list'),
    url(r'^page_list/$', page_list, name='PageAdmin-page_list'),
    url(r'^markup_help/$', markup_help, name='PageAdmin-markup_help'),
    url(r'^bulk_editor/$', bulk_editor, name='PageAdmin-bulk_editor'),
)
