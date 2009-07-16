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

from pylucid.models import PageContent
from pylucid.decorators import render_to


@render_to("page_update_list/PageUpdateTable.html")
def lucidTag(request, count=10):
    try:
        count = int(count)
    except Exception, e:
        # FIXME:
        request.user.message_set.create(message="page_update_list error: count must be a integer (%s)" % e)
        count = 10

    pages = PageContent.objects.order_by('-lastupdatetime')[:count]

    # TODO:
#    if not request.user.is_staff:
#        pages = pages.filter(showlinks = True)
#        pages = pages.exclude(permitViewPublic = False)
#
    return {"pages": pages}

