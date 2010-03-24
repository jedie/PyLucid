# coding:utf-8

"""
    PyLucid tag list
    ~~~~~~~~~~~~~~~~

    List all available lucidTag
"""

import inspect

from django.template import RequestContext
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.markup.django_tags import DjangoTagAssembler
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to


from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS
from pylucid_project.apps.pylucid.models import PageTree, PageMeta
from pylucid_project.utils.escape import escape

from page_admin.forms import SelectMarkupForm




@render_to("page_admin/page_list_popup.html")
@check_permissions(superuser_only=False, permissions=('pylucid.change_pagecontent',))
def page_list(request):
    """ Create a list of all existing lucidTag plugin views. """

    user = request.user
    tree = PageTree.objects.get_tree(user,
        filter_showlinks=False, exclude_plugin_pages=False)

    # add all PageMeta objects into tree
    tree.add_pagemeta(request)

    markup_id_str = None

    if request.method == 'GET':
        form = SelectMarkupForm(request.GET)
        if form.is_valid():
            markup_id_str = form.cleaned_data["markup"]
    else:
        form = SelectMarkupForm()

    context = {
        "title": "page list",
        "form": form,
        "markup_id_str": markup_id_str,
        "tree": tree,
    }
    return context


