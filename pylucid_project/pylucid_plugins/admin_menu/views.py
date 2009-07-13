# coding: utf-8

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from pylucid.models import PageTree

from pylucid_admin.models import PyLucidAdminPage


def lucidTag(request):
    """
    TODO: The admin menu should be build dynamic
    """
    if not request.user.is_authenticated():
        # Don't insert the admin top menu
        return

    pagetree = request.PYLUCID.pagetree # Current PageTree model instance
    if pagetree.type == PageTree.PLUGIN_TYPE:
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
        "admin_menu_link": reverse("admin_index"),
    }
    return render_to_response('admin_menu/admin_top_menu.html', context,
        context_instance=RequestContext(request)
    )

def panel_extras(request):
    items = PyLucidAdminPage.objects.all()
    output = []
    for item in items:
        output.append(
            '<li><a href="%s" title="%s">%s</a></li>' % (item.get_absolute_url(), item.title, item.name)
        )
    return "\n".join(output)
