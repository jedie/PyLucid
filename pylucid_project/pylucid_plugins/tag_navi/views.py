# -*- coding: utf-8 -*-

"""
    PyLucid tag navigation
    ~~~~~~~~~~~~~~~~~~~~~~
    
    A tag based navigation.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: 2009-03-31 15:03:20 +0200 (Di, 31 Mrz 2009) $
    $Rev: 1868 $
    $Author: JensDiemer $

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__ = "$Rev: 1868 $"

from django.utils.translation import ugettext as _

# http://code.google.com/p/django-tagging/
from tagging.models import Tag, TaggedItem

from pylucid_project.apps.pylucid.models import PageMeta
from pylucid_project.apps.pylucid.decorators import render_to



@render_to("tag_navi/tag_list.html")#, debug=True)
def http_get_view(request):
    tags = request.GET["tag_navi"]
    entries = TaggedItem.objects.get_by_model(PageMeta, tags)

    # add breadcrumb link
    context = request.PYLUCID.context
    breadcrumb_context_middlewares = context["context_middlewares"]["breadcrumb"]
    title = _("All '%s' tagged items" % tags)
    breadcrumb_context_middlewares.add_link(title, title, url=request.get_full_path())

    context = {
        "entries": entries,
        "tags": tags,
    }
    return context

@render_to("tag_navi/tag_link_list.html")#, debug=True)
def lucidTag(request):
    current_pagemeta = request.PYLUCID.pagemeta
    tags = current_pagemeta.tags
    context = {
        "pagemeta": current_pagemeta,
    }
    return context
