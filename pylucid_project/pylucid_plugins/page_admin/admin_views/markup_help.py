# coding:utf-8

"""
    PyLucid tag list
    ~~~~~~~~~~~~~~~~

    List all available lucidTag
    
    :copyleft: 2007-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from pylucid_project.apps.pylucid.markup import MARKUP_SHORT_DICT

from page_admin.forms import SelectMarkupForm


@render_to()
@check_permissions(superuser_only=False, permissions=('pylucid.change_pagecontent',))
def markup_help(request):
    """ Display a help page for a markup given via GET parameter """

    # Fallback: Use 'markup_help_base.html' template, if markup_id is wrong
    short_markup_name = "base"

    if request.method == 'GET':
        form = SelectMarkupForm(request.GET)
        if form.is_valid():
            markup_id = form.cleaned_data["markup_id"]
            short_markup_name = MARKUP_SHORT_DICT[markup_id]
    else:
        form = SelectMarkupForm()

    template_name = "page_admin/markup_help_%s.html" % short_markup_name

    context = {
        "template_name": template_name,
        "form_url": request.path,
        "form": form,
        "title": "%s markup help" % short_markup_name,
    }
    return context


