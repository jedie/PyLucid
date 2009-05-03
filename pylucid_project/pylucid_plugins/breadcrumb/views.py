# -*- coding: utf-8 -*-

"""
    PyLucid breadcrumb plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a horizontal backlink bar.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :created: 29.11.2005 10:14:02 by Jens Diemer
    :copyleft: 2005-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__= "$Rev$"

from django.template import RequestContext
from django.shortcuts import render_to_response

from pylucid_project.apps.pylucid.models import PageContent

from breadcrumb.preference_forms import BreadcumbPrefForm


def lucidTag(request):
    # Get preferences
    pref_form = BreadcumbPrefForm()
    pref_data = pref_form.get_preferences()
    
    # Get the current models.PageContent instance
    pagecontent = request.PYLUCID.pagecontent
    
    # Get all pages back to the root page as a list
    pagelist = PageContent.objects.get_backlist(request, pagecontent)

    context = {
        "preferences": pref_data,
        "pagelist": pagelist,
    }
    return render_to_response('breadcrumb/breadcrumb.html', context, 
        context_instance=RequestContext(request)
    )
