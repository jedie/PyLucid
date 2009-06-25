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
from django.conf.urls.defaults import patterns, url

from extrahead import admin_views

urlpatterns = patterns('',
    url(r'^view1$', admin_views.test1, name='extrahead-The view 1!'),
    url(r'^view2$', admin_views.test2, name='extrahead-The view 2!'),
)
