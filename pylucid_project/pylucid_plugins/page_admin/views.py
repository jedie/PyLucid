# coding: utf-8

"""
    PyLucid page admin
    ~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseRedirect

from pylucid_project.apps.pylucid.shortcuts import render_pylucid_response
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.decorators import check_permissions
from pylucid_project.apps.pylucid.models import PageTree, PageContent

from page_admin.forms import EditPageForm


def _get_pageobjects(request):
    """
    returns current PageContent instance.
    Note: In get views, the page content doesn't exist on PyLucid objects.
    """
    pagemeta = request.PYLUCID.pagemeta
    pagecontent = PageContent.objects.get(pagemeta=pagemeta)
    return pagemeta, pagecontent

def _edit_page(request, form_url):
    pagetree = request.PYLUCID.pagetree
    if pagetree.page_type != PageTree.PAGE_TYPE:
        request.page_msg("Current page is not a content page.")
        return

    pagemeta, pagecontent = _get_pageobjects(request)
    preview_html = ""

    if request.method == 'POST':
        edit_page_form = EditPageForm(request.POST)
        if edit_page_form.is_valid():
            if "preview" in request.POST:
                raw_content = edit_page_form.cleaned_data["content"]
                preview_html = apply_markup(
                    raw_content, pagecontent.markup, request.page_msg, escape_django_tags=True
                )
            else:
                new_content = edit_page_form.cleaned_data["content"]
                pagecontent.content = new_content
                pagecontent.save()
                request.page_msg.successful(_("Page content updated."))
                return HttpResponseRedirect(request.path)
    else:
        edit_page_form = EditPageForm(initial={"content":pagecontent.content})

    context = {
        "form_url": form_url,
        "abort_url": request.path,
        "preview_url": "%s?page_admin=preview" % request.path,

        "preview_html": preview_html,

        "markup_id_str": str(pagecontent.markup),

        "edit_page_form": edit_page_form,
        "pagecontent": pagecontent,
        "pagemeta": pagemeta,
    }
    return render_pylucid_response(request, 'page_admin/edit_inline_form.html', context,
        context_instance=RequestContext(request)
    )


def _edit_page_preview(request):
    """ AJAX preview """
    if request.method != 'POST':
        return HttpResponse("ERROR: Wrong request")
    edit_page_form = EditPageForm(request.POST)
    if not edit_page_form.is_valid():
        return HttpResponse("ERROR: Form not valid: %r" % edit_page_form.errors)
    content = edit_page_form.cleaned_data["content"]

    pagemeta, pagecontent = _get_pageobjects(request)

    raw_content = edit_page_form.cleaned_data["content"]
    html_content = apply_markup(raw_content, pagecontent.markup, request.page_msg, escape_django_tags=True)

    return HttpResponse(html_content)


@check_permissions(superuser_only=False,
    permissions=('pylucid.change_pagecontent', 'pylucid.change_pagemeta')
)
def http_get_view(request):
    action = request.GET["page_admin"]
    if action == "inline_edit":
        # replace the page content with the edit page form
        form_url = "%s?page_admin=inline_edit" % request.path
        return _edit_page(request, form_url)
    elif action == "preview":
        # preview via jQuery
        return _edit_page_preview(request)

    if settings.DEBUG:
        request.page_msg(_("Wrong get view parameter!"))
