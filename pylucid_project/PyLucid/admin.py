# -*- coding: utf-8 -*-
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

from PyLucid.models import Page, PageArchiv, Plugin, Preference, JS_LoginData,\
                                                                Style, Template


class JS_LoginDataAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'sha_checksum', 'salt', 'createtime', 'lastupdatetime'
    )

admin.site.register(JS_LoginData, JS_LoginDataAdmin)

#------------------------------------------------------------------------------

class PageAdmin(admin.ModelAdmin):
    list_display = (
        "id", "shortcut", "name", "title", "description",
        "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("shortcut",)
    list_filter = (
        "createby","lastupdateby","permitViewPublic", "template", "style"
    )
    date_hierarchy = 'lastupdatetime'
    search_fields = ["content", "name", "title", "description", "keywords"]

    # FIXME:
#    fields = (
#
#        ('meta', {'fields': ('keywords', 'description')}),
#        ('name / shortcut / title', {
#            'classes': 'collapse',
#            'fields': ('name','shortcut','title')
#        }),
#        ('template / style / markup', {
#            'classes': 'collapse',
#            'fields': ('template','style','markup')
#        }),
#        ('Advanced options', {
#            'classes': 'collapse',
#            'fields' : (
#                'showlinks', 'permitViewPublic',
#                'permitViewGroup', 'permitEditGroup'
#            ),
#        }),
#    )
#    fieldsets = (
#        ('basic', {'fields': ('content','parent','position',)}),
#    )


admin.site.register(Page, PageAdmin)


class PluginAdmin(admin.ModelAdmin):
    list_display = (
        "active", "plugin_name", "description", "can_deinstall"
    )
    list_display_links = ("plugin_name",)
    ordering = ('package_name', 'plugin_name')
    list_filter = ("author","package_name", "can_deinstall")

admin.site.register(Plugin, PluginAdmin)


class PageArchivAdmin(admin.ModelAdmin):
    list_display = (
        "id", "page", "edit_comment",
        "shortcut", "name", "title",
        "description", "lastupdatetime", "lastupdateby"
    )

admin.site.register(PageArchiv, PageArchivAdmin)

#------------------------------------------------------------------------------

class PreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "plugin", "comment",
    )
    list_display_links = ("comment",)
    ordering = ("plugin", "id")
    list_filter = ("plugin",)

admin.site.register(Preference, PreferenceAdmin)

#------------------------------------------------------------------------------

class StyleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "description", "createtime", "lastupdatetime"
    )
    list_display_links = ("name",)
    save_as = True

admin.site.register(Style, StyleAdmin)


class TemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    list_display_links = ("name",)
    save_as = True

admin.site.register(Template, TemplateAdmin)