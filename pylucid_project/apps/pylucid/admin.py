# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin

from reversion.admin import VersionAdmin

from pylucid import models
from pylucid.system.auto_model_info import UpdateInfoBaseAdmin


#------------------------------------------------------------------------------

class PageTreeAdmin(UpdateInfoBaseAdmin, VersionAdmin):
    #prepopulated_fields = {"slug": ("title",)}    

    list_display = (
        "slug", "get_absolute_url", "description",
        "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("slug", "get_absolute_url")
    list_filter = ("site", "type", "design", "createby", "lastupdateby", )
    date_hierarchy = 'lastupdatetime'
    search_fields = ("slug", "description")

admin.site.register(models.PageTree, PageTreeAdmin)


class LanguageAdmin(VersionAdmin):
    pass

admin.site.register(models.Language, LanguageAdmin)


class PageMetaAdmin(UpdateInfoBaseAdmin, VersionAdmin):
    list_display = ("title_or_slug", "get_absolute_url", "lastupdatetime", "lastupdateby",)
    list_display_links = ("title_or_slug", "get_absolute_url")
    list_filter = ("lang", "keywords", "createby", "lastupdateby")
    date_hierarchy = 'lastupdatetime'
    search_fields = ["description", "keywords"]

admin.site.register(models.PageMeta, PageMetaAdmin)


class PageContentAdmin(UpdateInfoBaseAdmin, VersionAdmin):
    list_display = ("title_or_slug", "get_absolute_url", "lastupdatetime", "lastupdateby",)
    list_display_links = ("title_or_slug", "get_absolute_url")
    list_filter = ("lang", "markup", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("content",)

admin.site.register(models.PageContent, PageContentAdmin)


class PluginPageAdmin(UpdateInfoBaseAdmin, VersionAdmin):
    list_display = ("get_plugin_name", "get_absolute_url", "app_label", "lastupdatetime", "lastupdateby",)
    list_display_links = ("get_plugin_name", "app_label")
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("app_label",)

admin.site.register(models.PluginPage, PluginPageAdmin)


class DesignAdmin(UpdateInfoBaseAdmin, VersionAdmin):    
    list_display = ("name", "template", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    list_filter = ("template", "createby", "lastupdateby")
    search_fields = ("name", "template")

admin.site.register(models.Design, DesignAdmin)


class EditableHtmlHeadFileAdmin(UpdateInfoBaseAdmin, VersionAdmin):
    list_display = ("filename", "description", "lastupdatetime", "lastupdateby")
    list_display_links = ("filename", "description")

admin.site.register(models.EditableHtmlHeadFile, EditableHtmlHeadFileAdmin)