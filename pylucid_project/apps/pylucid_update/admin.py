# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all old PyLucid model in django admin interface,
    but only in DEBUG mode.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.contrib import admin

from pylucid_project.apps.pylucid_update.models import Page08, Style08, Template08, \
                                        JS_LoginData08, BlogComment08, BlogTag, BlogEntry
from pylucid_project.apps.pylucid_admin.admin_site import pylucid_admin_site

#------------------------------------------------------------------------------

if settings.DEBUG: # Add v0.8 tables only in DEBUG mode.

    class JS_LoginDataAdmin(admin.ModelAdmin):
        list_display = (
            'user', 'sha_checksum', 'salt', 'createtime', 'lastupdatetime'
        )

    pylucid_admin_site.register(JS_LoginData08, JS_LoginDataAdmin)


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

    pylucid_admin_site.register(Page08, PageAdmin)


    #class PluginAdmin(admin.ModelAdmin):
    #    list_display = (
    #        "active", "plugin_name", "description", "can_deinstall"
    #    )
    #    list_display_links = ("plugin_name",)
    #    ordering = ('package_name', 'plugin_name')
    #    list_filter = ("author","package_name", "can_deinstall")
    #
    #pylucid_admin_site.register(Plugin, PluginAdmin)
    #
    #
    #class PageArchivAdmin(admin.ModelAdmin):
    #    list_display = (
    #        "id", "pagetree", "edit_comment",
    #        "shortcut", "name", "title",
    #        "description", "lastupdatetime", "lastupdateby"
    #    )
    #
    #pylucid_admin_site.register(PageArchiv, PageArchivAdmin)

    #------------------------------------------------------------------------------

    #class PreferenceAdmin(admin.ModelAdmin):
    #    list_display = (
    #        "id", "plugin", "comment",
    #    )
    #    list_display_links = ("comment",)
    #    ordering = ("plugin", "id")
    #    list_filter = ("plugin",)
    #
    #pylucid_admin_site.register(Preference, PreferenceAdmin)

    #------------------------------------------------------------------------------

    class StyleAdmin(admin.ModelAdmin):
        list_display = (
            "id", "name", "description", "createtime", "lastupdatetime"
        )
        list_display_links = ("name",)
        save_as = True

    pylucid_admin_site.register(Style08, StyleAdmin)


    class TemplateAdmin(admin.ModelAdmin):
        list_display = ("id", "name", "description")
        list_display_links = ("name",)
        save_as = True

    pylucid_admin_site.register(Template08, TemplateAdmin)


    #______________________________________________________________________________
    # Models from old Blog plugin

    class BlogComment08Admin(admin.ModelAdmin):
        pass
    pylucid_admin_site.register(BlogComment08, BlogComment08Admin)

    class BlogTagAdmin(admin.ModelAdmin):
        pass
    pylucid_admin_site.register(BlogTag, BlogTagAdmin)

    class BlogEntryAdmin(admin.ModelAdmin):
        pass
    pylucid_admin_site.register(BlogEntry, BlogEntryAdmin)
