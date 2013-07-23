# coding: utf-8

"""
    PyLucid admin url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf.urls import patterns, url

from pylucid_project.apps.pylucid.markup.views import markup_preview

from lexicon import admin_views

urlpatterns = patterns('',
    url(r'^new_lexicon_entry/$', admin_views.new_entry, name='Lexicon-new_entry'),
    url(r'^new_lexicon_entry/preview/$', markup_preview, name='Lexicon-markup_preview'),
)

