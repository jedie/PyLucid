# coding:utf-8

"""
    PyLucid tag list
    ~~~~~~~~~~~~~~~~

    List all available lucidTag
"""

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from pylucid_project.apps.pylucid.markup.hightlighter import get_pygments_css
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

    # get the EditableHtmlHeadFile path to pygments.css (page_msg created, if not exists)
    pygments_css_path = get_pygments_css(request)

    context = {
        "template_name": template_name,
        "form_url": request.path,
        "form": form,
        "title": "%s markup help" % short_markup_name,
        "pygments_css": pygments_css_path,
    }
    return context


