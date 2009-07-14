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
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin

from reversion.admin import VersionAdmin

from pylucid import models

#_____________________________________________________________________________
# Some work-a-rounds for django bugs :(

# Quick work-a-round for http://code.djangoproject.com/ticket/10061
admin.site.root_path = "/%s/" % settings.ADMIN_URL_PREFIX

#-----------------------------------------------------------------------------
# add user brocken, if TEMPLATE_STRING_IF_INVALID != ""
# http://code.djangoproject.com/ticket/11176
from django.contrib.auth.admin import UserAdmin

org_add_view = UserAdmin.add_view
def ugly_patched_add_view(*args, **kwargs):
    old = settings.TEMPLATE_STRING_IF_INVALID
    settings.TEMPLATE_STRING_IF_INVALID = ""
    result = org_add_view(*args, **kwargs)
    settings.TEMPLATE_STRING_IF_INVALID = old
    return result

UserAdmin.add_view = ugly_patched_add_view


#------------------------------------------------------------------------------

class PermissionAdmin(admin.ModelAdmin):
    """ django auth Permission """
    list_display = ("id", "name", "content_type", "codename")
    list_display_links = ("name", "codename")
    list_filter = ("content_type",)
admin.site.register(Permission, PermissionAdmin)

#------------------------------------------------------------------------------




class PageTreeAdmin(VersionAdmin):
    #prepopulated_fields = {"slug": ("title",)}    

    list_display = ("id", "parent", "slug", "site", "get_absolute_url", "lastupdatetime", "lastupdateby")
    list_display_links = ("slug", "get_absolute_url")
    list_filter = ("site", "page_type", "design", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("slug",)

admin.site.register(models.PageTree, PageTreeAdmin)


class LanguageAdmin(VersionAdmin):
    pass

admin.site.register(models.Language, LanguageAdmin)


class PageMetaAdmin(VersionAdmin):
    list_display = ("id", "title_or_slug", "get_absolute_url", "get_site", "lastupdatetime", "lastupdateby",)
    list_display_links = ("title_or_slug", "get_absolute_url")
    list_filter = ("lang", "keywords", "createby", "lastupdateby")
    date_hierarchy = 'lastupdatetime'
    search_fields = ("description", "keywords")


admin.site.register(models.PageMeta, PageMetaAdmin)

class PageContentInline(admin.StackedInline):
    model = models.PageContent

class PageContentAdmin(VersionAdmin):
    list_display = ("id", "title_or_slug", "get_absolute_url", "get_site", "lastupdatetime", "lastupdateby",)
    list_display_links = ("title_or_slug", "get_absolute_url")
    list_filter = ("lang", "markup", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("content", "title_or_slug", "get_absolute_url")

admin.site.register(models.PageContent, PageContentAdmin)


class PluginPageAdmin(VersionAdmin):
    list_display = (
        "id", "get_plugin_name", "get_absolute_url", "app_label",
        "get_site", "lastupdatetime", "lastupdateby",
    )
    list_display_links = ("get_plugin_name", "app_label")
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("app_label",)

admin.site.register(models.PluginPage, PluginPageAdmin)

#-----------------------------------------------------------------------------

#class ColorAdmin(VersionAdmin):
#    list_display = ("id", "name","value")
#admin.site.register(models.Color, ColorAdmin)

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

admin.site.register(models.ColorScheme, ColorSchemeAdmin)


class DesignAdmin(VersionAdmin):
    list_display = ("id", "name", "template", "colorscheme", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    list_filter = ("site", "template", "colorscheme", "createby", "lastupdateby")
    search_fields = ("name", "template", "colorscheme")

admin.site.register(models.Design, DesignAdmin)


class EditableHtmlHeadFileAdmin(VersionAdmin):
    list_display = ("id", "filepath", "render", "description", "lastupdatetime", "lastupdateby")
    list_display_links = ("filepath", "description")
    list_filter = ("site", "render")

admin.site.register(models.EditableHtmlHeadFile, EditableHtmlHeadFileAdmin)

#-----------------------------------------------------------------------------

class UserProfileAdmin(VersionAdmin):
    list_display = ("id", "user", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("user",)
    list_filter = ("site",)

admin.site.register(models.UserProfile, UserProfileAdmin)
