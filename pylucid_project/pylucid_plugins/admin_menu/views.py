# coding: utf-8

from django.conf import settings
from django.core import urlresolvers
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from pylucid.models import PageTree
from pylucid.decorators import render_to

from pylucid_admin.models import PyLucidAdminPage

@render_to("admin_menu/admin_top_menu.html")
def lucidTag(request):
    """
    Render the pylucid admin menu, if the user is authentivated.
    """
    if not request.user.is_authenticated():
        # Don't insert the admin top menu
        return

    pagetree = request.PYLUCID.pagetree # Current PageTree model instance
    if pagetree.page_type == PageTree.PLUGIN_TYPE:
        edit_admin_panel_link = reverse("admin_pylucid_pagetree_change", args=(pagetree.id,))
    else:
        pagecontent = request.PYLUCID.pagecontent
        edit_admin_panel_link = reverse("admin_pylucid_pagecontent_change", args=(pagecontent.id,))

    pagemeta = request.PYLUCID.pagemeta # Current PageMeta model instance
    edit_meta_admin_panel_link = reverse("admin_pylucid_pagemeta_change", args=(pagemeta.id,))

    context = {
        "logout_link": "?auth=logout",

        "edit_page_link": "?page_admin=inline_edit",

        "edit_admin_panel_link": edit_admin_panel_link,
        "edit_meta_admin_panel_link": edit_meta_admin_panel_link,
        "new_page_link": reverse("admin_pylucid_pagecontent_add"),
    }
    return context


def panel_extras(request):
    """
    returns all PyLucid admin menu items with can the current user use.
    Used in the inline admin menu and for the pylucid admin menu in the django admin panel.
    
    Usage in template:
        {% lucidTag admin_menu.panel_extras %}
        
    TODO: Use a tree generator to build a real tree menu
    """
    items = PyLucidAdminPage.objects.get_for_user(request.user)
    output = []
    for item in items:
        if not item.get_absolute_url():
            # FIXME: Skip the section entries
            # TODO: This should be removed, if a tree can be build!
            continue
        output.append(
            '<li><a href="%s" title="%s">%s</a></li>' % (item.get_absolute_url(), item.title, item.name)
        )
    return "\n".join(output)
