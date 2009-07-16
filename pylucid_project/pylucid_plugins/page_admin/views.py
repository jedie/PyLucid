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

from pylucid.markup.converter import apply_markup
from pylucid.shortcuts import render_pylucid_response
from pylucid.decorators import check_permissions

from page_admin.forms import EditPageForm



def _edit_page(request, form_url):
    pagemeta_instance = request.PYLUCID.pagemeta
    pagecontent_instance = request.PYLUCID.pagecontent

    if request.method == 'POST':
        edit_page_form = EditPageForm(request.POST)
        if edit_page_form.is_valid():
            new_content = edit_page_form.cleaned_data["content"]
            pagecontent_instance.content = new_content
            pagecontent_instance.save()
            request.page_msg.successful(_("Page content updated."))
            return HttpResponseRedirect(request.path)
    else:
        edit_page_form = EditPageForm({"content":pagecontent_instance.content})

    context = {
        "form_url": form_url,
        "abort_url": request.path,
        "preview_url": "%s?page_admin=preview" % request.path,

        "pagelinklist_url": "#TODO", #FIXME ;)
        "taglist_url": "#TODO", #FIXME ;)

        "edit_page_form": edit_page_form,
        "pagecontent_instance": pagecontent_instance,
        "pagemeta_instance": pagemeta_instance,
    }
    return render_pylucid_response(request, 'page_admin/edit_page_form.html', context,
        context_instance=RequestContext(request)
    )


def _edit_page_preview(request):
    """ AJAX preview """
    if request.method != 'POST':
        return HttpResponse("ERROR: Wrong request")
    edit_page_form = EditPageForm(request.POST)
    if not edit_page_form.is_valid():
        return HttpResponse("ERROR: Form not valid!")
    content = edit_page_form.cleaned_data["content"]

    pagecontent_instance = request.PYLUCID.pagecontent
    pagecontent_instance.content = edit_page_form.cleaned_data["content"]
    html_content = apply_markup(pagecontent_instance, request.page_msg)

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
