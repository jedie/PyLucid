# -*- coding: utf-8 -*-

"""
    PyLucid page update list plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a list of the latest page updates.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__ = "$Rev$"

from django.conf import settings

from pylucid.decorators import render_to

from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS

from models import UpdateJournal



@render_to("update_journal/update_journal_table.html")
def lucidTag(request, count=10):
    try:
        count = int(count)
    except Exception, e:
        if request.user.is_stuff():
            request.page_msg.error("page_update_list error: count must be a integer (%s)" % e)
        count = 10

    queryset = UpdateJournal.on_site.all()
    if not request.user.is_staff:
        queryset = queryset.filter(staff_only=False)

    queryset = queryset[:count]

    return {"update_list": queryset}

