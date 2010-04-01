# -*- coding: utf-8 -*-

"""
    PyLucid superfish main menu
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2009-09-10 14:56:24 +0200 (Do, 10. Sep 2009) $
    $Rev: 2330 $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__ = "$Rev: 2330 $"


from pylucid_project.apps.pylucid.models import PageTree, PageMeta, PageContent, Language
from pylucid_project.apps.pylucid.decorators import render_to


@render_to("sf_main_menu/sf_main_menu.html")
def lucidTag(request, min=1, max=0):
    """ Create the superfish main menu """
    user = request.user
    current_lang = request.PYLUCID.current_language
    current_pagetree = request.PYLUCID.pagetree

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
        # mark the current url tree
        tree.set_current_node(first_showlink.id, delete_hidden=False)
    except KeyError, err:
        tree.set_current_node(None, delete_hidden=False) # Root node
        if settings.DEBUG:
            request.page_msg.error("Can't activate menu item %r KeyError: %s" % (current_pagetree, err))
            request.page_msg("tree nodes: %r" % tree.nodes)
            request.page_msg("All PageTree:", PageTree.objects.all())
            request.page_msg("Current user:", request.user)
            request.page_msg("all accessible PageTree:", PageTree.objects.all_accessible(request.user).all())

    # make all nodes visible
    tree.activate_all()

    tree.slice_menu(min, max)

    # add all PageMeta objects into tree
    tree.add_pagemeta(request)

    #tree.debug()

    return {"nodes": tree.get_first_nodes()}
