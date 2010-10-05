# coding:utf-8

"""
    PyLucid tag list
    ~~~~~~~~~~~~~~~~

    List all available lucidTag
"""

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.models import PageTree

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

    markup_id = None

    if request.method == 'GET':
        form = SelectMarkupForm(request.GET)
        if form.is_valid():
            markup_id = form.cleaned_data["markup_id"]
    else:
        form = SelectMarkupForm()

    context = {
        "title": "page list",
        "form": form,
        "form_url": request.path,
        "markup_id": markup_id,
        "tree": tree,
    }
    return context


