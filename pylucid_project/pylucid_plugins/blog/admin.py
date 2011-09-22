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
from pylucid_project.apps.pylucid.markup.admin import MarkupPreview

from pylucid_project.pylucid_plugins.blog.models import BlogEntry, \
    BlogEntryContent


class BlogEntryAdmin(admin.ModelAdmin):
    """
    Language independend Blog entry.
    """
    list_display = ("id", "site_info",)
    list_filter = ("sites",)
admin.site.register(BlogEntry, BlogEntryAdmin)


class BlogEntryContentAdmin(BaseAdmin, MarkupPreview, VersionAdmin):
    """
    Language depend blog entry content.
    
    inherited attributes from BaseAdmin:
        view_on_site_link -> html link with the absolute uri.
        
    inherited from MarkupPreview:
        ajax_markup_preview() -> the markup content ajax preview view
        get_urls()            -> add ajax view to admin urls 
    """
    list_display = ("id", "headline", "is_public", "view_on_site_link", "lastupdatetime", "lastupdateby")
    list_display_links = ("headline",)
    list_filter = ("is_public", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("headline", "content")
    ordering = ('-lastupdatetime',)

admin.site.register(BlogEntryContent, BlogEntryContentAdmin)
