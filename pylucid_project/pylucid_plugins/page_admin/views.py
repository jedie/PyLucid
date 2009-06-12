# coding:utf-8

import warnings

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from pylucid.markup.converter import apply_markup

from page_admin.forms import EditPageForm


EDIT_PERMISSIONS = (
    "pylucid.can_edit_page",
    "pylucid.can_edit_pagemeta",
)


def check_permissions(request, permissions):
    user = request.user
    if user.has_perms(permissions):
        return
    
    if settings.DEBUG: # Usefull??
        for permission in permissions:
            if not user.has_perm(permission):
                warnings.warn("User %r has not the permission: %r" % (user, permission))
    
    raise PermissionDenied


def _edit_page(request, render_function):
    check_permissions(request, EDIT_PERMISSIONS)
    
    pagemeta_instance = request.PYLUCID.pagemeta
    pagecontent_instance = request.PYLUCID.pagecontent
    
    if request.method == 'POST':
        edit_page_form = EditPageForm(request.POST)
        if edit_page_form.is_valid():
            new_content = edit_page_form.cleaned_data["content"]
            pagecontent_instance.content = new_content
            pagecontent_instance.save(request)
            request.page_msg.successful(_("Page content updated."))
            return HttpResponseRedirect(request.path)
    else:
        edit_page_form = EditPageForm({"content":pagecontent_instance.content})
    
    context = {
        "form_url": "%s?page_admin=inline_edit" % request.path,
        "abort_url": request.path,
        "preview_url": "%s?page_admin=preview" % request.path,
        "edit_page_form": edit_page_form,
        "pagecontent_instance": pagecontent_instance,
        "pagemeta_instance": pagemeta_instance,
    }
    return render_function('page_admin/edit_page_form.html', context, 
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


def http_get_view(request):  
    action = request.GET["page_admin"]
    if action=="inline_edit":
        # replace the page content with the edit page form
        return _edit_page(request, render_function=render_to_string)
    elif action=="get_ajax_form":
        # return the edit page form only, for inserting it via jQuery
        return _edit_page(request, render_function=render_to_response)
    elif action=="preview":
        # preview via jQuery
        return _edit_page_preview(request)
    
    if settings.DEBUG:
        request.page_msg(_("Wrong get view parameter!"))