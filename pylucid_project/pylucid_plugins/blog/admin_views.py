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
from pylucid.decorators import check_permissions, render_to

from pylucid_admin.admin_menu import AdminMenu

from blog.forms import BlogEntryForm



def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("create content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="Blog-new_blog_entry",
        name="new blog entry", title="Create a new blog entry.",
    )

    return "\n".join(output)



@check_permissions(superuser_only=False, permissions=("blog.add_blogentry",))
@render_to("blog/new_blog_entry.html")
def new_blog_entry(request):
    """
    TODO:
    """
    if request.method == "POST":
        form = BlogEntryForm(request.POST)
        if form.is_valid():
            instance = form.save()
            request.page_msg("blog entry saved.")
            return http.HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = BlogEntryForm()

    context = {
        "title": "Create a new blog entry",
        "form_url": request.path,
        "form": form,
    }
    return context

