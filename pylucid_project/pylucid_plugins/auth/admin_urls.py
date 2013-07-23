# coding: utf-8

"""
    auth pylucid admin url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls import patterns, url

from pylucid_project.pylucid_plugins.auth.admin_views import profile_index, JS_password_change
from django.contrib.auth.views import password_change, password_change_done

urlpatterns = patterns('',
    url(r'^profile_index/$', profile_index, name='Auth-profile_index'),
    url(r'^JS_password_change/$', JS_password_change, name='Auth-JS_password_change'),

    # Fallback plaintext password change views from django:
    url(r'^plaintext_password_change/$', password_change, name='Auth-plaintext_password_change'),
    url(r'^plaintext_password_change_done/$', password_change_done, name='Auth-plaintext_password_change_done'),
)
