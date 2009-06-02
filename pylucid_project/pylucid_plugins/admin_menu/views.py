# coding: utf-8

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response


def lucidTag(request):
    context = {
        "logout_link": "?auth=logout",
        "edit_page_link": "TODO",
        "new_page_link": "TODO",
        "admin_menu_link": reverse("admin_index"),
    }
    return render_to_response('admin_menu/admin_top_menu.html', context, 
        context_instance=RequestContext(request)
    )