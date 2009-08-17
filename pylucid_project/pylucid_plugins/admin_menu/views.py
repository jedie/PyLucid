# coding: utf-8

from django.conf import settings
from django.core import urlresolvers
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from pylucid.models import PageTree, PluginPage
from pylucid.decorators import render_to

from pylucid_admin.models import PyLucidAdminPage

@render_to("admin_menu/admin_top_menu.html")#, debug=True)
def lucidTag(request):
    """
    Render the pylucid admin menu, if the user is authenticated.
    """
    if not request.user.is_authenticated():
        # Don't insert the admin top menu
        return

    context = {
        "inline": True,
        "logout_link": "?auth=logout",
        "edit_page_link": "?page_admin=inline_edit",
        "new_page_link": reverse("admin:pylucid_pagecontent_add"),
    }
    return context


@render_to("admin_menu/admin_menu_items.html")
def panel_extras(request):
    """
    returns all PyLucid admin menu items with can the current user use.
    Used in the inline admin menu and for the pylucid admin menu in the django admin panel.
    
    Usage in template:
        {% lucidTag admin_menu.panel_extras %}
    """
    tree = PyLucidAdminPage.objects.get_tree()
    #tree.debug()
    nodes = tree.get_first_nodes()
    return {"nodes":nodes}

