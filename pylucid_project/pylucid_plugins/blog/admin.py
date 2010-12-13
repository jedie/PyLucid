# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf.urls.defaults import patterns
from django.contrib import admin

from reversion.admin import VersionAdmin

from pylucid_project.apps.pylucid.base_admin import BaseAdmin

from blog.models import BlogEntry

from pylucid_project.apps.pylucid.markup.admin import MarkupPreview


class BlogEntryAdmin(BaseAdmin, MarkupPreview, VersionAdmin):
    """
    inherited attributes from BaseAdmin:
        view_on_site_link -> html link with the absolute uri.
        
    inherited from MarkupPreview:
        ajax_markup_preview() -> the markup content ajax preview view
        get_urls()            -> add ajax view to admin urls 
    """
    list_display = ("id", "headline", "is_public", "view_on_site_link", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("headline",)
    list_filter = ("is_public", "sites", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("headline", "content")
    ordering = ('-lastupdatetime',)



admin.site.register(BlogEntry, BlogEntryAdmin)
