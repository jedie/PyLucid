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

from internals import admin_views

urlpatterns = patterns('',
    url(r'^show_internals/$', admin_views.show_internals, name='Internal-show_internals'),
    url(r'^model_graph/$', admin_views.model_graph, name='Internal-model_graph'),
    url(r'^form_generator/$', admin_views.form_generator, name='Internal-form_generator'),
    url(r'^form_generator/(?P<model_no>\d+?)/$', admin_views.form_generator, name='Internal-form_generator'),
)
