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
from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS

from pylucid_project.apps.pylucid.decorators import superuser_only

plugin_admin_urls = PYLUCID_PLUGINS.get_admin_urls()

urlpatterns = patterns('',
    url(r'^menu/$', views.menu, name='PyLucidAdmin-menu'),

    url(r'^plugins/', include(plugin_admin_urls)),

    url(r'^install/pylucid/$', superuser_only(views.install_pylucid), name='PyLucidAdmin-install_pylucid'),
    url(r'^install/plugins/$', superuser_only(views.install_plugins), name='PyLucidAdmin-install_plugins'),
)
