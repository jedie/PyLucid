# coding: utf-8

"""
    PyLucid admin menu
    ~~~~~~~~~~~~~~~~~~
    
    The PyLucid admin menu, build with superfish
    
    superfish homepage:
        http://users.tpg.com.au/j_birch/plugins/superfish/
    
    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $
    
    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.conf import settings
from django.core import urlresolvers
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.models import PageTree, PluginPage, Language
from pylucid_project.apps.pylucid.decorators import render_to

from pylucid_project.apps.pylucid_admin.models import PyLucidAdminPage


@render_to("admin_menu/admin_top_menu.html")#, debug=True)
def lucidTag(request):
    """
    Render the pylucid admin menu, if the user is authenticated.
    example: {% lucidTag admin_menu %}
    """
    if not request.user.is_authenticated():
        # Don't insert the admin top menu
        return

    lang_count = Language.objects.count()

    context = {
        "inline": True,
        "logout_link": "?auth=logout",
        "edit_page_link": "?page_admin=inline_edit",
        "new_page_link": reverse("admin:pylucid_pagecontent_add"),
        "add_translate": lang_count > 1,
    }
    return context


def panel_extras(request):
    """
    returns all PyLucid admin menu items with can the current user use.
    Used in the inline admin menu and for the pylucid admin menu in the django admin panel.
    
    Usage in template with:
        {% lucidTag admin_menu.panel_extras %}
    """
    user = request.user

    tree = PyLucidAdminPage.objects.get_tree_for_user(user)
    #tree.debug()
    nodes = tree.get_first_nodes()

    context = {"nodes":nodes}
    response = render_to_response(
        "admin_menu/admin_menu_items.html", context, context_instance=RequestContext(request)
    )
    return response

