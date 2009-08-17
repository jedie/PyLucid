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

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

from pylucid.models import PageTree, PageMeta, PageContent
from pylucid.decorators import render_to


@render_to("main_menu/main_menu.html")
def lucidTag(request, min=1, max=0):
    """
    TODO: use min, max options!
    """
    current_lang = request.PYLUCID.lang_entry
    current_pagetree = request.PYLUCID.pagetree
    user = request.user

    # Get a pylucid.tree_model.TreeGenerator instance with all accessible PageTree for the current user
    tree = PageTree.objects.get_tree(user, filter_showlinks=True)

    # activate the current pagetree node (for main menu template)
    def get_first_showlink(pagetree):
        """ returns the first pagetree witch has showlinks==True, go recursive up to next parent """
        if pagetree.showlinks == False and pagetree.parent != None:
            return get_first_showlink(pagetree.parent)
        return pagetree

    first_showlink = get_first_showlink(current_pagetree)
    try:
        tree.set_current_node(first_showlink.id)
    except KeyError, err:
        tree.set_current_node(None) # Root node
        if settings.DEBUG:
            request.page_msg.error("Can't activate menu item %r KeyError: %s" % (current_pagetree, err))
            request.page_msg("tree nodes: %r" % tree.nodes)
            request.page_msg("All PageTree:", PageTree.objects.all())
            request.page_msg("Current user:", request.user)
            request.page_msg("all accessible PageTree:", PageTree.objects.all_accessible(request.user).all())

    tree.slice_menu(min, max)

    # add all PageMeta objects into tree
    tree.add_pagemeta(request)

#    # add all PageMeta objects into tree
#    queryset = PageMeta.objects.filter(lang=current_lang)
#
#    tree.add_related(queryset, field="page", attrname="pagemeta")
#    #tree.debug()

    return {"nodes": tree.get_first_nodes()}











