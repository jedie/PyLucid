# -*- coding: utf-8 -*-

"""
    PyLucid sub_menu plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a link list of all sub pages.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author$

    :copyleft: 2005-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__= "$Rev$"

from django.template import RequestContext
from django.shortcuts import render_to_response

from pylucid_project.apps.pylucid.models import PageContent


def lucidTag(request): 
    # Get the current models.PageContent instance
    pagecontent = request.PYLUCID.pagecontent
      
    sub_pages = PageContent.objects.get_sub_pages(pagecontent)

    context = {
        "sub_pages": sub_pages,
    }
    return render_to_response('sub_menu/sub_menu.html', context, 
        context_instance=RequestContext(request)
    )










