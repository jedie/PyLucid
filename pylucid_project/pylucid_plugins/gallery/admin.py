# coding: utf-8

"""
    Gallery PyLucid Plugin - admin 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Register model in django admin interface.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin
from django import forms

from pylucid_project.apps.pylucid.models import PageTree, PluginPage
from pylucid_project.apps.pylucid.base_admin import BaseAdmin

from django_tools.widgets import SelectMediaPath

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
        choices = [
            (page.pagetree.id, page.pagetree.get_absolute_url())
            for page in plugin_pages
        ]
        self.fields["pagetree"].choices = choices

        # Select a sub directory in settings.MEDIA_ROOT
        self.fields["path"].widget = SelectMediaPath()


class GalleryModelAdmin(BaseAdmin):
    form = GalleryAdminForm
    list_display = (
        "view_on_site_link", "path",
        "lastupdatetime", "lastupdateby"
    )
#    list_display_links = ("destination_url", "response_type")
#    list_filter = ("response_type", "full_url", "append_query_string", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
#    search_fields = ("destination_url",)

admin.site.register(GalleryModel, GalleryModelAdmin)
