# coding: utf-8

"""
    PyLucid app url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls.defaults import patterns, url

from pylucid_project.apps.pylucid.views import root_page, lang_root_page, resolve_url

urlpatterns = patterns('',
    url(r'^$', root_page, name='PyLucid-root_page'),
    url(r'^(?P<lang_code>[a-zA-Z-_]{2,}?)/$', lang_root_page, name='PyLucid-lang_root_page'),
    url(r'^(?P<lang_code>[a-zA-Z-_]{2,}?)/(?P<url_path>[\w/-]+?)/$', resolve_url, name='PyLucid-resolve_url'),
)
