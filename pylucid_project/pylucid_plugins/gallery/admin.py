# coding: utf-8

"""
    Gallery PyLucid Plugin - admin 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Register model in django admin interface.

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.http import HttpResponseRedirect
from django.contrib import admin
from django import forms

# https://github.com/jedie/django-reversion-compare
from reversion_compare.admin import CompareVersionAdmin

from pylucid_project.apps.pylucid.models import PageTree, PluginPage
from pylucid_project.apps.pylucid.base_admin import BaseAdmin, RedirectToPageAdmin

from gallery.models import GalleryModel



class GalleryAdminForm(forms.ModelForm):
    """
    Filter pagetree selection.
    Add only pagetree items witch are a gallery plugin page.
    """
    class Meta:
        model = GalleryModel

    def __init__(self, *args, **kwargs):
        super(GalleryAdminForm, self).__init__(*args, **kwargs)

        plugin_pages = PluginPage.objects.filter(app_label="pylucid_project.pylucid_plugins.gallery")
        # TODO: Filter pagetree's witch has already a Gallery PluginPage
        choices = [
            (page.pagetree.id, page.pagetree.get_absolute_url())
            for page in plugin_pages
        ]
        self.fields["pagetree"].choices = choices


class GalleryModelAdmin(RedirectToPageAdmin, BaseAdmin, CompareVersionAdmin):
    form = GalleryAdminForm
    list_display = (
        "view_on_site_link", "path", "template",
        "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("path",)
    list_filter = ("template", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    #search_fields = ("path", "template",)

admin.site.register(GalleryModel, GalleryModelAdmin)
