# coding: utf-8

"""
    Redirect PyLucid Plugin - admin 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Register model in django admin interface.

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin
from django import forms

from pylucid_project.apps.pylucid.models import PluginPage
from pylucid_project.apps.pylucid.base_admin import BaseAdmin

# https://github.com/jedie/django-reversion-compare
from reversion_compare.admin import CompareVersionAdmin

from redirect.models import RedirectModel


class RedirectAdminForm(forms.ModelForm):
    """
    Filter pagetree selection.
    Add only pagetree items witch are a redirect plugin page.
    """
    class Meta:
        model = RedirectModel

    def __init__(self, *args, **kwargs):
        super(RedirectAdminForm, self).__init__(*args, **kwargs)

        plugin_pages = PluginPage.objects.filter(app_label="pylucid_project.pylucid_plugins.redirect")

        choices = [
            (page.pagetree.id, page.pagetree.get_absolute_url())
            for page in plugin_pages
        ]
        self.fields["pagetree"].choices = choices


class RedirectModelAdmin(BaseAdmin, CompareVersionAdmin):
    form = RedirectAdminForm

    list_display = (
        "view_on_site_link", "destination_url", "response_type", "full_url", "append_query_string",
        "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("destination_url", "response_type")
    list_filter = ("response_type", "full_url", "append_query_string", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("destination_url",)

admin.site.register(RedirectModel, RedirectModelAdmin)
