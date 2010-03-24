# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    TODO:
        * if http://code.djangoproject.com/ticket/3400 is implement:
            Add site to list_filter for e.g. PageMeta, PageContent etc.      
    
    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from reversion.admin import VersionAdmin

from pylucid import models
from pylucid_project.apps.pylucid.base_admin import BaseAdmin

from pylucid_project.apps.pylucid_admin.admin_site import pylucid_admin_site


class PageTreeAdmin(BaseAdmin, VersionAdmin):
    #prepopulated_fields = {"slug": ("title",)}
    list_display = (
        "id", "parent", "slug", "showlinks", "site", "view_on_site_link", "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("id", "slug")
    list_filter = (
        "site", "page_type", "permitViewGroup", "showlinks", "createby", "lastupdateby", "design",
    )
    date_hierarchy = 'lastupdatetime'
    search_fields = ("slug",)

pylucid_admin_site.register(models.PageTree, PageTreeAdmin)


class BanEntryAdmin(admin.ModelAdmin):
    list_display = list_display_links = ("ip_address", "createtime",)
    search_fields = ("ip_address",)
pylucid_admin_site.register(models.BanEntry, BanEntryAdmin)


class LanguageAdmin(VersionAdmin):
    list_display = ("code", "description", "site_info", "permitViewGroup")
    list_display_links = ("code", "description")
    list_filter = ("permitViewGroup",)
pylucid_admin_site.register(models.Language, LanguageAdmin)


class LogEntryAdmin(BaseAdmin):
    list_display = ("createtime", "createby", "view_on_site_link", "app_label", "action", "message")
    list_filter = (
        "site", "app_label", "action", "createby"
    )
    search_fields = ("app_label", "action", "message", "long_message", "data")
pylucid_admin_site.register(models.LogEntry, LogEntryAdmin)


#class OnSitePageMeta(models.PageMeta):
#    def get_site(self):
#        return self.page.site
#    site = property(get_site)
#    class Meta:
#        proxy = True



class PageMetaAdmin(BaseAdmin, VersionAdmin):
    list_display = ("id", "get_title", "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",)
    list_display_links = ("id", "get_title")
    list_filter = ("language", "createby", "lastupdateby", "tags")#"keywords"
    date_hierarchy = 'lastupdatetime'
    search_fields = ("description", "keywords")

pylucid_admin_site.register(models.PageMeta, PageMetaAdmin)


class PageContentInline(admin.StackedInline):
    model = models.PageContent

class PageContentAdmin(BaseAdmin, VersionAdmin):
    list_display = ("id", "get_title", "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",)
    list_display_links = ("id", "get_title")
    list_filter = ("markup", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("content",) # it would be great if we can add "get_title"

pylucid_admin_site.register(models.PageContent, PageContentAdmin)


class PluginPageAdmin(BaseAdmin, VersionAdmin):
    list_display = (
        "id", "get_plugin_name", "app_label",
        "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",
    )
    list_display_links = ("get_plugin_name", "app_label")
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("app_label",)

pylucid_admin_site.register(models.PluginPage, PluginPageAdmin)

#-----------------------------------------------------------------------------

#class ColorAdmin(VersionAdmin):
#    list_display = ("id", "name","value")
#pylucid_admin_site.register(models.Color, ColorAdmin)

class ColorInline(admin.TabularInline):
    model = models.Color
    extra = 0

class ColorSchemeAdmin(VersionAdmin):
    list_display = ("id", "name", "preview", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("sites",)
    inlines = [ColorInline, ]

    def preview(self, obj):
        colors = models.Color.objects.all().filter(colorscheme=obj)
        result = ""
        for color in colors:
            result += '<span style="background-color:#%s;" title="%s">&nbsp;&nbsp;&nbsp;</span>' % (
                color.value, color.name
            )
        return result
    preview.short_description = 'color preview'
    preview.allow_tags = True

pylucid_admin_site.register(models.ColorScheme, ColorSchemeAdmin)


class DesignAdmin(VersionAdmin):
    list_display = ("id", "name", "template", "colorscheme", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    list_filter = ("sites", "template", "colorscheme", "createby", "lastupdateby")
    search_fields = ("name", "template", "colorscheme")

pylucid_admin_site.register(models.Design, DesignAdmin)


class EditableHtmlHeadFileAdmin(VersionAdmin):
    list_display = ("id", "filepath", "site_info", "render", "description", "lastupdatetime", "lastupdateby")
    list_display_links = ("filepath", "description")
    list_filter = ("sites", "render")

pylucid_admin_site.register(models.EditableHtmlHeadFile, EditableHtmlHeadFileAdmin)

#-----------------------------------------------------------------------------

class UserProfileAdmin(VersionAdmin):
    list_display = ("id", "user", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("user",)
    list_filter = ("sites",)

pylucid_admin_site.register(models.UserProfile, UserProfileAdmin)
