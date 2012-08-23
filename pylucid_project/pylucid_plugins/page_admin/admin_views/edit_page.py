# coding:utf-8

"""
    edit a content/plugin page
    ~~~~~~~~~~~~~~~~~~~
    
    Edit a content page:
        form with: PageTree, PageMeta and PageContent at once.
        
    Edit a plugin page:
        form with: PageTree, PageMeta and PluginPage at once.    
    
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import http
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.models import PageTree, PageMeta, PageContent, Language, PluginPage

from page_admin.forms import PageTreeForm, PageMetaForm, PageContentForm, PluginPageForm
from django.shortcuts import get_object_or_404


@check_permissions(superuser_only=False, permissions=("pylucid.change_pagecontent",))
def _edit_content_page(request, context, pagetree):
    """ edit a PageContent """
    default_lang_entry = Language.objects.get_or_create_default(request)
    pagemeta = PageTree.objects.get_pagemeta(request, pagetree, show_lang_errors=True)
    pagecontent = PageContent.objects.get(pagemeta=pagemeta)

    if request.method != "POST":
        pagetree_form = PageTreeForm(instance=pagetree)
        pagemeta_form = PageMetaForm(instance=pagemeta, prefix=default_lang_entry.code)
        pagecontent_form = PageContentForm(instance=pagecontent)
    else:
        if "cancel" in request.POST:
            url = pagecontent.get_absolute_url()
            messages.info(request, _("Edit content page (%s) aborted, ok.") % url)
            return http.HttpResponseRedirect(url)

        pagetree_form = PageTreeForm(request.POST, instance=pagetree)
        pagemeta_form = PageMetaForm(request.POST, instance=pagemeta, prefix=default_lang_entry.code)
        pagecontent_form = PageContentForm(request.POST, instance=pagecontent)
        if not (pagetree_form.is_valid() and pagemeta_form.is_valid() and pagecontent_form.is_valid()):
            context["has_errors"] = True
        else:
            # All forms are valid -> Save all.
            sid = transaction.savepoint()
            try:
                pagetree_form.save()
                pagemeta_form.save()
                pagecontent_form.save()
            except:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                messages.info(request, _("Content page %r updated.") % pagecontent)
                return http.HttpResponseRedirect(pagecontent.get_absolute_url())

    # A list of all existing forms -> for form errorlist
    all_forms = [pagecontent_form, pagemeta_form, pagetree_form]

    context.update({
        "title": _("Edit a content page"),
        "template_name": "page_admin/edit_content_page.html",
        "default_lang_entry": default_lang_entry,
        "pagecontent": pagecontent,

        "markup_id_str": str(pagecontent.markup),

        "all_forms": all_forms, # For display the form error list from all existing forms.

        "pagetree_form": pagetree_form,
        "pagemeta_form":pagemeta_form,
        "pagecontent_form": pagecontent_form,
    })
    return context


@check_permissions(superuser_only=False, permissions=("pylucid.change_pluginpage",))
def _edit_plugin_page(request, context, pagetree):
    """ edit a PluginPage entry with PageMeta in all Languages """

    pagemetas = PageMeta.objects.filter(pagetree=pagetree)
    pluginpage = PluginPage.objects.get(pagetree=pagetree)

    if request.method == "POST" and "cancel" in request.POST:
        url = pluginpage.get_absolute_url()
        messages.info(request, _("Edit plugin page (%s) aborted, ok.") % url)
        return http.HttpResponseRedirect(url)

    # Create for every language a own PageMeta model form.
    pagemeta_formset = []
    pagemeta_is_valid = True # Needed for check if all forms are valid.
    for pagemeta in pagemetas:
        if request.method == "POST":
            form = PageMetaForm(request.POST, prefix=pagemeta.language.code, instance=pagemeta)
            if not form.is_valid():
                pagemeta_is_valid = False
        else:
            form = PageMetaForm(prefix=pagemeta.language.code, instance=pagemeta)
        form.language = pagemeta.language # for language info in fieldset legend
        pagemeta_formset.append(form)

    if request.method == "POST":
        pagetree_form = PageTreeForm(request.POST, instance=pagetree)
        pluginpage_form = PluginPageForm(request.POST, instance=pluginpage)
        if pagemeta_is_valid and pagetree_form.is_valid() and pluginpage_form.is_valid():
            sid = transaction.savepoint()
            try:
                pagetree_form.save()
                pluginpage_form.save()

                # Save all PageMeta entries and attach them to PluginPage
                new_pluginpage_instance = []
                for pagemeta_form in pagemeta_formset:
                    pagemeta_form.save()
            except:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                messages.info(request, _("Plugin page %r updated.") % pluginpage)
                return http.HttpResponseRedirect(pluginpage.get_absolute_url())
    else:
        pagetree_form = PageTreeForm(instance=pagetree)
        pluginpage_form = PluginPageForm(instance=pluginpage)

    # A list of all existing forms -> for form errorlist
    all_forms = pagemeta_formset[:] + [pluginpage_form, pagetree_form]

    context = {
        "title": _("Edit a plugin page"),
        "template_name": "page_admin/edit_plugin_page.html",

        "all_forms": all_forms, # For display the form error list from all existing forms.
        "has_errors": request.method == "POST", # At least one form has errors.
        # The forms:
        "pluginpage_form": pluginpage_form,
        "pagetree_form": pagetree_form,
        "pagemeta_formset": pagemeta_formset,
    }
    return context


@check_permissions(superuser_only=False, permissions=("pylucid.change_pagetree", "pylucid.change_pagemeta"))
@render_to()
def edit_page(request, pagetree_id=None):
    """
    edit a PageContent or a PluginPage.
    """
    pagetree = get_object_or_404(PageTree, id=pagetree_id)
    context = {"form_url": request.path}

    is_pluginpage = pagetree.page_type == PageTree.PLUGIN_TYPE
    if is_pluginpage:
        return _edit_plugin_page(request, context, pagetree)
    else:
        return _edit_content_page(request, context, pagetree)
