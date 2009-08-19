# coding: utf-8

from django.conf import settings
from django.core import urlresolvers
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.utils.safestring import mark_safe

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


def panel_extras(request):
    """
    returns all PyLucid admin menu items with can the current user use.
    Used in the inline admin menu and for the pylucid admin menu in the django admin panel.
    
    Usage in template with:
        {% lucidTag admin_menu.panel_extras %}
        
    Note: The cache would be "cleared" in PyLucidAdminPage.save()
    """
    user = request.user
    cache_key = "panel_extras_%s" % user.pk
    response = cache.get(cache_key)
    if response:
        return response

    tree = PyLucidAdminPage.objects.get_tree_for_user(user)
    #tree.debug()
    nodes = tree.get_first_nodes()

    context = {"nodes":nodes}
    response = render_to_response(
        "admin_menu/admin_menu_items.html", context, context_instance=RequestContext(request)
    )
    cache.set(cache_key, response)
    return response

