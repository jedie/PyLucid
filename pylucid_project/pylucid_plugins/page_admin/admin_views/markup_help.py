# coding:utf-8

"""
    PyLucid tag list
    ~~~~~~~~~~~~~~~~

    List all available lucidTag
"""

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from pylucid_project.apps.pylucid.markup.hightlighter import get_pygments_css
from pylucid_project.apps.pylucid.models import PageContent

from page_admin.forms import SelectMarkupHelpForm


@render_to()
@check_permissions(superuser_only=False, permissions=('pylucid.change_pagecontent',))
def markup_help(request):
    """ Display a help page for a markup given via GET parameter """

    #~ MARKUP_CREOLE = 6
    #~ MARKUP_HTML = 0
    #~ MARKUP_HTML_EDITOR = 1
    #~ MARKUP_TINYTEXTILE = 2
    #~ MARKUP_TEXTILE = 3
    #~ MARKUP_MARKDOWN = 4
    #~ MARKUP_REST = 5

    # Fallback: Use 'markup_help_base.html' template, if markup_id is wrong
    short_markup_name = "base"

    if request.method == 'GET':
        form = SelectMarkupHelpForm(request.GET)
        if form.is_valid():
            markup_id = form.cleaned_data["markup"]
            short_markup_name = PageContent.MARKUP_SHORT_DICT[markup_id]
    else:
        form = SelectMarkupHelpForm()

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


