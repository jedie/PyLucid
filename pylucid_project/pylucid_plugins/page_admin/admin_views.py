# coding:utf-8

from django import forms, http
from django.db import transaction
from django.core import urlresolvers
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from pylucid_project.utils.form_utils import make_kwargs

from pylucid.models import PageTree, PageMeta, PageContent, Design, Language, PluginPage
from pylucid.preference_forms import SystemPreferencesForm
from pylucid.decorators import check_permissions, render_to

from pylucid_admin.admin_menu import AdminMenu

from page_admin.forms import PageContentForm, PluginPageForm


EDIT_PLUGIN_TEMPLATE = "page_admin/edit_plugin_page.html"
EDIT_CONTENT_TEMPLATE = "page_admin/edit_content_page.html"



def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("create content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="PageAdmin-new_content_page",
        name="new content page", title="Create a new content page.",
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="PageAdmin-new_plugin_page",
        name="new plugin page", title="Create a new plugin page.",
    )

    return "\n".join(output)



@check_permissions(superuser_only=False,
    permissions=("pylucid.add_pagecontent", "pylucid.add_pagemeta", "pylucid.add_pagetree")
)
@render_to(EDIT_CONTENT_TEMPLATE)
def new_content_page(request):
    """
    Create a new content page.
    
    TODO:
        * setup design via ajax, if not set and a parent page tree was selected
        * Auto generate slug from page name with javascript
    
    
    can use django.forms.models.inlineformset_factory:
        PageFormSet = inlineformset_factory(PageTree, PageContent, PageMeta)
    get:
        metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of
        the metaclasses of all its bases
    see also: http://code.djangoproject.com/ticket/7837
    """
    if request.method == "POST":
        form = PageContentForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            sid = transaction.savepoint()
            try:
                pagetree_instance = PageTree.objects.easy_create(cleaned_data,
                    extra={"page_type": PageTree.PAGE_TYPE}
                )
                pagemeta_instance = PageMeta.objects.easy_create(cleaned_data,
                    extra={"page": pagetree_instance}
                )
                pagecontent_instance = PageContent.objects.easy_create(cleaned_data,
                    extra={"page": pagetree_instance, "pagemeta": pagemeta_instance}
                )
            except:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                request.page_msg("New page %r created." % pagecontent_instance)
                return http.HttpResponseRedirect(pagecontent_instance.get_absolute_url())
    else:
        form = PageContentForm()

    context = {
        "title": "Create a new page",
        "form_url": request.path,
        "form": form,
    }
    return context



@check_permissions(superuser_only=False,
    permissions=("pylucid.add_pluginpage", "pylucid.add_pagemeta", "pylucid.add_pagetree")
)
@render_to(EDIT_PLUGIN_TEMPLATE)
def new_plugin_page(request):
    """
    Create a new plugin page.
    TODO: add in form all PageMeta fields in all existing languages.
    """
    if request.method == "POST":
        form = PluginPageForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            sid = transaction.savepoint()
            created_pluginpages = []
            try:
                pagetree_instance = PageTree.objects.easy_create(cleaned_data,
                    extra={"page_type": PageTree.PLUGIN_TYPE}
                )
                # Create plugin page in every language
                for lang in Language.objects.all():
                    pagemeta_instance = PageMeta.objects.easy_create(cleaned_data,
                        extra={"page": pagetree_instance, "lang": lang}
                    )
                    pluginpage_instance = PluginPage.objects.easy_create(cleaned_data,
                        extra={"page": pagetree_instance, "pagemeta": pagemeta_instance, "lang": lang}
                    )
                    created_pluginpages.append(pluginpage_instance)
            except:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                request.page_msg("New plugin page %r created." % created_pluginpages)
                return http.HttpResponseRedirect(pagetree_instance.get_absolute_url())
    else:
        form = PluginPageForm()

    context = {
        "title": "Create a new plugin page",
        "form_url": request.path,
        "form": form,
    }
    return context


@check_permissions(superuser_only=False,
    permissions=("pylucid.change_pagemeta", "pylucid.change_pagetree")
)
@render_to()
def edit_page(request, pagetree_id=None):
    """
    edit a PageContent or a PluginPage.
    """
    request.page_msg("TODO: Implement the save routine.")
    request.page_msg("FIXME: Why does the form not fill all existing data, e.g: design, parent fields etc.")

    if not pagetree_id:
        raise

    pagetree = PageTree.objects.get(id=pagetree_id)

    context = {}

    is_pluginpage = pagetree.page_type == PageTree.PLUGIN_TYPE

    if is_pluginpage:
        if not request.user.has_perms("pylucid.change_pluginpage"):
            raise PermissionDenied("You have not the permission to change a plugin page!")
        Form = PluginPageForm
        context.update({
            "title": "Edit plugin page",
            "template_name": EDIT_PLUGIN_TEMPLATE,
        })
    else:
        if not request.user.has_perms("pylucid.change_pagecontent"):
            raise PermissionDenied("You have not the permission to change a content page!")
        Form = PageContentForm
        context.update({
            "title": "Edit content page",
            "template_name": EDIT_CONTENT_TEMPLATE,
        })

    if request.method == "POST":
        form = Form(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            request.page_msg(cleaned_data)
    else:
        pagemeta = PageTree.objects.get_pagemeta(request, pagetree, show_lang_info=True)
        form_models = [pagetree, pagemeta]
        if is_pluginpage:
            pluginpage = PluginPage.objects.get(page=pagetree)
            form_models.append(pluginpage)
        else:
            pagecontent = PageTree.objects.get_pagecontent(request, pagetree, show_lang_info=True)
            form_models.append(pagecontent)

        form_base_fields = Form.base_fields.keys()
        form_data = {}
        for model in form_models:
            keys = model._meta.get_all_field_names()
            for key in keys:
                if key not in form_base_fields:
                    continue
                value = getattr(model, key)
                #request.page_msg("*", key, value)
                form_data[key] = value

        form = Form(initial=form_data)

#    from django.forms.models import inlineformset_factory
#    FormSet = inlineformset_factory(PageTree, PageMeta, extra=1)
#    form = FormSet(instance=pagetree)

    context.update({
        "form_url": request.path,
        "form": form,
    })
    return context
