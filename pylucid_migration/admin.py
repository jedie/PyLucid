# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    TODO:
        * if http://code.djangoproject.com/ticket/3400 is implement:
            Add site to list_filter for e.g. PageMeta, PageContent etc.
        * split this file
    
    :copyleft: 2008-2016 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

from django import forms
from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.admin.utils import unquote
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-reversion-compare
from reversion_compare.admin import CompareVersionAdmin

from pylucid_migration import models


def register(model_class, admin_class):
    try:
        admin.site.register(model_class, admin_class)
    except admin.sites.AlreadyRegistered: # registered by pylucid.admin
        admin.site.unregister(model_class)
        admin.site.register(model_class, admin_class)


class PageTreeAdmin(CompareVersionAdmin):
    #prepopulated_fields = {"slug": ("title",)}
    list_display = (
        "id", "parent", "slug", "showlinks", "site", "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("id", "slug")
    list_filter = (
        "site", "page_type", "permitViewGroup", "showlinks", "createby", "lastupdateby", "design",
    )
    date_hierarchy = 'lastupdatetime'
    search_fields = ("slug",)

    def delete_view(self, request, object_id, extra_context=None):
        """
        Redirect to parent page, after deletion.
        """
        if request.POST: # The user has already confirmed the deletion.
            pagetree = self.get_object(request, unquote(object_id))
            parent = pagetree.parent

        response = super(PageTreeAdmin, self).delete_view(request, object_id, extra_context)
        if request.POST and isinstance(response, HttpResponseRedirect):
            # Object has been deleted.
            if parent is None:
                url = "/"
            else:
                url = parent.get_absolute_url()
            return HttpResponseRedirect(url)

        return response

register(models.PageTree, PageTreeAdmin)


class BanEntryAdmin(admin.ModelAdmin):
    list_display = list_display_links = ("ip_address", "createtime",)
    search_fields = ("ip_address",)
register(models.BanEntry, BanEntryAdmin)


class LanguageAdmin(CompareVersionAdmin):
    list_display = ("code", "description", "site_info", "permitViewGroup")
    list_display_links = ("code", "description")
    list_filter = ("permitViewGroup",)
register(models.Language, LanguageAdmin)


class LogEntryAdmin(admin.ModelAdmin):
    def age(self, obj):
        """ view on site link in admin changelist, try to use complete uri with site info. """
        createtime = obj.createtime
        return timesince(createtime)

    age.short_description = _("age")

    list_display = (
        "createtime", "age", "createby", "app_label", "action", "message"
    )
    list_filter = (
        "site", "app_label", "action", "createby", "remote_addr",
    )
    search_fields = ("app_label", "action", "message", "long_message", "data")
register(models.LogEntry, LogEntryAdmin)


#class OnSitePageMeta(models.PageMeta):
#    def get_site(self):
#        return self.page.site
#    site = property(get_site)
#    class Meta:
#        proxy = True



class PageMetaAdmin(CompareVersionAdmin):
    list_display = ("id", "get_title", "get_site", "lastupdatetime", "lastupdateby",)
    list_display_links = ("id", "get_title")
    list_filter = ("language", "createby", "lastupdateby", "tags")#"keywords"
    date_hierarchy = 'lastupdatetime'
    search_fields = ("description", "keywords")

register(models.PageMeta, PageMetaAdmin)


class PageContentInline(admin.StackedInline):
    model = models.PageContent

class PageContentAdmin(CompareVersionAdmin):
    list_display = ("id", "get_title", "get_site", "lastupdatetime", "lastupdateby",)
    list_display_links = ("id", "get_title")
    list_filter = ("markup", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("content",) # it would be great if we can add "get_title"

register(models.PageContent, PageContentAdmin)


class PluginPageAdmin(CompareVersionAdmin):
    list_display = (
        "id", "get_plugin_name", "app_label",
        "get_site", "lastupdatetime", "lastupdateby",
    )
    list_display_links = ("get_plugin_name", "app_label")
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("app_label",)

register(models.PluginPage, PluginPageAdmin)


#------------------------------------------------------------------------------


class ColorAdmin(CompareVersionAdmin):
    def preview(self, obj):
        return '<span style="background-color:#%s;" title="%s">&nbsp;&nbsp;&nbsp;</span>' % (
            obj.value, obj.name
        )
    preview.short_description = 'color preview'
    preview.allow_tags = True

    # disable delete all admin actions
    # User should not use delete colors, because model.delete() would
    # not called, read "warning" box on:
    # http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/
    actions = None

    list_display = ("id", "name", "value", "preview", "colorscheme")
    list_filter = ("colorscheme",)

register(models.Color, ColorAdmin)

class ColorInline(admin.TabularInline):
    model = models.Color
    extra = 0


class ColorSchemeAdmin(CompareVersionAdmin):
    list_display = ("id", "name", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = [ColorInline, ]

register(models.ColorScheme, ColorSchemeAdmin)



class DesignAdmin(CompareVersionAdmin):
    list_display = ("id", "name", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    ordering = ("name",)
    list_filter = ("sites", "template", "colorscheme", "createby", "lastupdateby")
    search_fields = ("name", "template", "colorscheme")

register(models.Design, DesignAdmin)


#------------------------------------------------------------------------------


class EditableHtmlHeadFileAdmin(CompareVersionAdmin):
    list_display = ("id", "filepath", "render", "description", "lastupdatetime", "lastupdateby")
    list_display_links = ("filepath", "description")
    list_filter = ("render",)

register(models.EditableHtmlHeadFile, EditableHtmlHeadFileAdmin)


#-----------------------------------------------------------------------------


class UserProfileAdmin(CompareVersionAdmin):
    list_display = ("id", "user", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("user",)
    list_filter = ("sites",)
    actions = ["set_site"]

register(models.UserProfile, UserProfileAdmin)

