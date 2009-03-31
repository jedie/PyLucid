# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all old PyLucid model in django admin interface.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin

from pylucid_project.apps.pylucid_update.models import Page08, Style08, Template08


#------------------------------------------------------------------------------

class PageAdmin(admin.ModelAdmin):
    list_display = (
        "id", "shortcut", "name", "title", "description",
        "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("shortcut",)
    list_filter = (
        "createby", "lastupdateby", "permitViewPublic", "showlinks",
        "template", "style", "markup",
    )
    date_hierarchy = 'lastupdatetime'
    search_fields = ["content", "name", "title", "description", "keywords"]

admin.site.register(Page08, PageAdmin)


#class PluginAdmin(admin.ModelAdmin):
#    list_display = (
#        "active", "plugin_name", "description", "can_deinstall"
#    )
#    list_display_links = ("plugin_name",)
#    ordering = ('package_name', 'plugin_name')
#    list_filter = ("author","package_name", "can_deinstall")
#
#admin.site.register(Plugin, PluginAdmin)
#
#
#class PageArchivAdmin(admin.ModelAdmin):
#    list_display = (
#        "id", "page", "edit_comment",
#        "shortcut", "name", "title",
#        "description", "lastupdatetime", "lastupdateby"
#    )
#
#admin.site.register(PageArchiv, PageArchivAdmin)

#------------------------------------------------------------------------------

#class PreferenceAdmin(admin.ModelAdmin):
#    list_display = (
#        "id", "plugin", "comment",
#    )
#    list_display_links = ("comment",)
#    ordering = ("plugin", "id")
#    list_filter = ("plugin",)
#
#admin.site.register(Preference, PreferenceAdmin)

#------------------------------------------------------------------------------

class StyleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "description", "createtime", "lastupdatetime"
    )
    list_display_links = ("name",)
    save_as = True

admin.site.register(Style08, StyleAdmin)


class TemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    list_display_links = ("name",)
    save_as = True

admin.site.register(Template08, TemplateAdmin)