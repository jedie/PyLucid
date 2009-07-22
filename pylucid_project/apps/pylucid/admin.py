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

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.conf import settings

from reversion.admin import VersionAdmin

from pylucid import models

from pylucid_admin.admin import pylucid_admin_site



if settings.DEBUG:
    class PermissionAdmin(admin.ModelAdmin):
        """ django auth Permission """
        list_display = ("id", "name", "content_type", "codename")
        list_display_links = ("name", "codename")
        list_filter = ("content_type",)
    pylucid_admin_site.register(Permission, PermissionAdmin)

    class ContentTypeAdmin(admin.ModelAdmin):
        """ django ContentType """
        list_display = list_display_links = ("id", "app_label", "name", "model")
        list_filter = ("app_label",)
    pylucid_admin_site.register(ContentType, ContentTypeAdmin)

#------------------------------------------------------------------------------




class PageTreeAdmin(VersionAdmin):
    #prepopulated_fields = {"slug": ("title",)}    

    list_display = ("id", "parent", "slug", "site", "get_absolute_url", "lastupdatetime", "lastupdateby")
    list_display_links = ("slug", "get_absolute_url")
    list_filter = ("site", "page_type", "design", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("slug",)

pylucid_admin_site.register(models.PageTree, PageTreeAdmin)


class LanguageAdmin(VersionAdmin):
    pass

pylucid_admin_site.register(models.Language, LanguageAdmin)


class PageMetaAdmin(VersionAdmin):
    list_display = ("id", "get_title", "get_absolute_url", "get_site", "lastupdatetime", "lastupdateby",)
    list_display_links = ("get_title", "get_absolute_url")
    list_filter = ("lang", "keywords", "createby", "lastupdateby")
    date_hierarchy = 'lastupdatetime'
    search_fields = ("description", "keywords")


pylucid_admin_site.register(models.PageMeta, PageMetaAdmin)

class PageContentInline(admin.StackedInline):
    model = models.PageContent

class PageContentAdmin(VersionAdmin):
    list_display = ("id", "get_title", "get_absolute_url", "get_site", "lastupdatetime", "lastupdateby",)
    list_display_links = ("get_title", "get_absolute_url")
    list_filter = ("lang", "markup", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("content", "get_title", "get_absolute_url")

pylucid_admin_site.register(models.PageContent, PageContentAdmin)


class PluginPageAdmin(VersionAdmin):
    list_display = (
        "id", "get_plugin_name", "get_absolute_url", "app_label",
        "get_site", "lastupdatetime", "lastupdateby",
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

class ColorSchemeAdmin(VersionAdmin):
    list_display = ("id", "name", "preview", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    search_fields = ("name",)
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
    list_display = ("id", "name", "template", "colorscheme", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    list_filter = ("site", "template", "colorscheme", "createby", "lastupdateby")
    search_fields = ("name", "template", "colorscheme")

pylucid_admin_site.register(models.Design, DesignAdmin)


class EditableHtmlHeadFileAdmin(VersionAdmin):
    list_display = ("id", "filepath", "render", "description", "lastupdatetime", "lastupdateby")
    list_display_links = ("filepath", "description")
    list_filter = ("site", "render")

pylucid_admin_site.register(models.EditableHtmlHeadFile, EditableHtmlHeadFileAdmin)

#-----------------------------------------------------------------------------

class UserProfileAdmin(VersionAdmin):
    list_display = ("id", "user", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("user",)
    list_filter = ("site",)

pylucid_admin_site.register(models.UserProfile, UserProfileAdmin)
