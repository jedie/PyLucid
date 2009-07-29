# -*- coding: utf-8 -*-

"""
    PyLucid sub_menu plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a link list of all sub pages.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: 2009-04-29 14:36:54 +0200 (Mi, 29. Apr 2009) $
    $Rev: 1934 $
    $Author: JensDiemer $

    :copyleft: 2005-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev: 1934 $"

from django.template import RequestContext
from django.shortcuts import render_to_response

from pylucid.models import PageTree, PageMeta, PageContent
from pylucid.decorators import render_to


@render_to("main_menu/main_menu.html")
def lucidTag(request):
    current_lang = request.PYLUCID.lang_entry
    current_pagetree = request.PYLUCID.pagetree

    tree = PageTree.objects.get_tree()

    # activate the current pagetree node (for main menu template)
    tree.set_current_node(current_pagetree.id)

    # add all PageMeta objects into tree
    queryset = PageMeta.objects.all().filter(lang=current_lang)

    # Filter PageTree view permissions:
    if request.user.is_anonymous(): # Anonymous user are in no user group
        queryset = queryset.filter(page__permitViewGroup=None)
    elif not request.user.is_superuser: # Superuser can see everything ;)
        queryset = queryset.filter(page__permitViewGroup__in=request.user.groups)

    tree.add_related(queryset, field="page", attrname="pagemeta")
    #tree.debug()

    return {"nodes": tree.get_first_nodes()}











