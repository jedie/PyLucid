# -*- coding: utf-8 -*-

"""
    PyLucid main_menu plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a tree menu.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: 2009-04-29 14:36:54 +0200 (Mi, 29. Apr 2009) $
    $Rev: 1934 $
    $Author: JensDiemer $

    :copyleft: 2005-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev: 1934 $"

from django.conf import settings

from pylucid_project.apps.pylucid.models import PageTree
from pylucid_project.apps.pylucid.decorators import render_to


def _debug(request, tree):
    request.page_msg("tree nodes: %r" % tree.nodes)
    request.page_msg("All PageTree:", PageTree.objects.all())
    request.page_msg("Current user:", request.user)
    request.page_msg("all accessible PageTree:", PageTree.objects.all_accessible(request.user).all())


@render_to("main_menu/main_menu.html")
def lucidTag(request, min=1, max=0):
    """
    You can split the menu with the optional min and max arguments:
    * min - The starting level (first level is 1)
    * max - The end level (without end, use 0)
    
    more info:
    http://www.pylucid.org/permalink/132/the-main-menu-plugin
    
    example:
        {% lucidTag main_menu %}
        {% lucidTag main_menu min=1 max=1 %}
        {% lucidTag main_menu min=2 max=0 %}
    """
    current_pagetree = request.PYLUCID.pagetree
    user = request.user

    # Get a pylucid.tree_model.TreeGenerator instance with all accessible PageTree for the current user
    tree = PageTree.objects.get_tree(user, filter_showlinks=True)

    # activate the current pagetree node (for main menu template)
    def get_first_showlink(pagetree):
        """ returns the first pagetree witch has showlinks==True, go recursive up to next parent """
        if pagetree.showlinks == False:
            if pagetree.parent == None:
                # not parent page available -> activate root node
                return None
            else:
                # go recursive up to next parent
                return get_first_showlink(pagetree.parent)
        return pagetree.id

    first_showlink_id = get_first_showlink(current_pagetree)
    try:
        tree.set_current_node(first_showlink_id)
    except KeyError, err:
        tree.set_current_node(None) # Root node
        if settings.DEBUG:
            request.page_msg.error("Can't activate menu item %r KeyError: %s" % (current_pagetree, err))
            _debug(request, tree)

    tree.slice_menu(min, max)

    # add all PageMeta objects into tree
    tree.add_pagemeta(request)

#    _debug(request, tree)

    return {"nodes": tree.get_first_nodes()}











