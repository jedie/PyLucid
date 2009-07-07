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
from django.conf.urls.defaults import patterns, url, include

from pylucid_project.apps.pylucid_admin import views
from pylucid_project.utils import pylucid_plugins

urlpatterns = patterns('',
    url(r'^menu/$', views.menu, name='PyLucidAdmin-menu'),

    url(r'^pylucid/', include(pylucid_plugins.PLUGINS.get_admin_urls())),

    url(r'^install/pylucid/$', views.install_pylucid, name='PyLucidAdmin-install_pylucid'),
    url(r'^install/plugins/$', views.install_plugins, name='PyLucidAdmin-install_plugins'),
)
