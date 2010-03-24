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

from update_journal.admin_views import cleanup

urlpatterns = patterns('',
    url(r'^cleanup/$', cleanup, name='UpdateJournal-cleanup'),
)

