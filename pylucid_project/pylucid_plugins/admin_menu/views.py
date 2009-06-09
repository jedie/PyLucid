# coding: utf-8

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from pylucid.models import PageTree


def lucidTag(request):
    if not request.user.is_authenticated():
        # Don't insert the admin top menu
        return  
    
    pagetree = request.PYLUCID.pagetree
    if pagetree.type == PageTree.PLUGIN_TYPE:
        edit_admin_panel_link = reverse("admin_pylucid_pagetree_change", args=(pagetree.id,))
    else:
        pagecontent = request.PYLUCID.pagecontent
        edit_admin_panel_link = reverse("admin_pylucid_pagecontent_change", args=(pagecontent.id,))
        
    # Get the pagemeta instance for the current pagetree and language
    pagemeta = PageTree.objects.get_pagemeta(request)
        
    edit_meta_admin_panel_link = reverse("admin_pylucid_pagemeta_change", args=(pagemeta.id,))
    
    context = {
        "logout_link": "?auth=logout",
        "edit_page_link": "TODO",
        "edit_admin_panel_link": edit_admin_panel_link,
        "edit_meta_admin_panel_link": edit_meta_admin_panel_link,
        "new_page_link": reverse("admin_pylucid_pagecontent_add"),
        "admin_menu_link": reverse("admin_index"),
    }
    return render_to_response('admin_menu/admin_top_menu.html', context, 
        context_instance=RequestContext(request)
    )