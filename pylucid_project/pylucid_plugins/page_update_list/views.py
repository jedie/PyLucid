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

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__= "$Rev$"

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from pylucid_project.apps.pylucid.models import PageContent

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
    context = {"pages": pages}

    return render_to_response('page_update_list/PageUpdateTable.html', context, 
        context_instance=RequestContext(request)
    )

