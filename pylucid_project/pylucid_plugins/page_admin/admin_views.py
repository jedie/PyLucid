# coding:utf-8

from django import forms, http
from django.db import transaction
from django.core import urlresolvers
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _

from pylucid_project.utils.form_utils import make_kwargs

from pylucid.models import PageTree, PageMeta, PageContent, Design, Language, PluginPage
from pylucid.preference_forms import SystemPreferencesForm

from pylucid_admin.admin_menu import AdminMenu

from page_admin.forms import PageContentForm, PluginPageForm






def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("create content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="new content page", title="Create a new content page.",
        url_name="PageAdmin-new_content_page"
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="new plugin page", title="Create a new plugin page.",
        url_name="PageAdmin-new_plugin_page"
    )

    return "\n".join(output)




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
    return render_to_response('page_admin/new_content_page.html', context,
        context_instance=RequestContext(request)
    )


def new_plugin_page(request):
    """
    Create a new plugin page.
    """
    if request.method == "POST":
        form = PluginPageForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            sid = transaction.savepoint()
            try:
                pagetree_instance = PageTree.objects.easy_create(cleaned_data,
                    extra={"page_type": PageTree.PLUGIN_TYPE}
                )
                pagemeta_instance = PageMeta.objects.easy_create(cleaned_data,
                    extra={"page": pagetree_instance}
                )
                pagecontent_instance = PluginPage.objects.easy_create(cleaned_data,
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
        form = PluginPageForm()

    context = {
        "title": "Create a new plugin page",
        "form_url": request.path,
        "form": form,
    }
    return render_to_response('page_admin/new_content_page.html', context,
        context_instance=RequestContext(request)
    )
