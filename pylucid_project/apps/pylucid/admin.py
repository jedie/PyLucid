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

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from reversion.admin import VersionAdmin

from pylucid import models
from pylucid_project.apps.pylucid.base_admin import BaseAdmin



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

admin.site.register(models.PageTree, PageTreeAdmin)


class BanEntryAdmin(admin.ModelAdmin):
    list_display = list_display_links = ("ip_address", "createtime",)
    search_fields = ("ip_address",)
admin.site.register(models.BanEntry, BanEntryAdmin)


class LanguageAdmin(VersionAdmin):
    list_display = ("code", "description", "site_info", "permitViewGroup")
    list_display_links = ("code", "description")
    list_filter = ("permitViewGroup",)
admin.site.register(models.Language, LanguageAdmin)


class LogEntryAdmin(BaseAdmin):
    list_display = ("createtime", "createby", "view_on_site_link", "app_label", "action", "message")
    list_filter = (
        "site", "app_label", "action", "createby"
    )
    search_fields = ("app_label", "action", "message", "long_message", "data")
admin.site.register(models.LogEntry, LogEntryAdmin)


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

admin.site.register(models.PageMeta, PageMetaAdmin)


class PageContentInline(admin.StackedInline):
    model = models.PageContent

class PageContentAdmin(BaseAdmin, VersionAdmin):
    list_display = ("id", "get_title", "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",)
    list_display_links = ("id", "get_title")
    list_filter = ("markup", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("content",) # it would be great if we can add "get_title"

admin.site.register(models.PageContent, PageContentAdmin)


class PluginPageAdmin(BaseAdmin, VersionAdmin):
    list_display = (
        "id", "get_plugin_name", "app_label",
        "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",
    )
    list_display_links = ("get_plugin_name", "app_label")
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("app_label",)

admin.site.register(models.PluginPage, PluginPageAdmin)


#------------------------------------------------------------------------------


class ColorSchemeAdminForm(forms.ModelForm):
    class Meta:
        model = models.ColorScheme

    def clean_sites(self):
        """
        Check if headfile sites contain the site from all design entries.
        """
        sites = self.cleaned_data["sites"]
        designs = models.Design.objects.all().filter(headfiles=self.instance)
        for design in designs:
            for design_site in design.sites.all():
                if design_site in sites:
                    continue
                raise forms.ValidationError(_(
                    "ColorScheme must exist on site %(site)r!"
                    " Because it's used by design %(design)r." % {
                        "site": design_site,
                        "design": design
                    }
                ))

        return sites


if settings.DEBUG:
    class ColorAdmin(VersionAdmin):
        def preview(self, obj):
            return '<span style="background-color:#%s;" title="%s">&nbsp;&nbsp;&nbsp;</span>' % (
                obj.value, obj.name
            )
        preview.short_description = 'color preview'
        preview.allow_tags = True

        list_display = ("id", "name", "value", "preview")
        list_filter = ("colorscheme",)

    admin.site.register(models.Color, ColorAdmin)

class ColorInline(admin.TabularInline):
    model = models.Color
    extra = 0


class ColorSchemeAdmin(VersionAdmin):
    form = ColorSchemeAdminForm
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

admin.site.register(models.ColorScheme, ColorSchemeAdmin)


#------------------------------------------------------------------------------


class DesignAdminForm(forms.ModelForm):
    class Meta:
        model = models.Design

    def clean(self):
        """
        check if all headfiles and colorscheme exist on the same site
        than the design exist.
        """
        cleaned_data = self.cleaned_data

        if "sites" not in cleaned_data: # e.g. no sites selected
            return cleaned_data
        sites = cleaned_data["sites"]

        if "headfiles" not in cleaned_data: # e.g. no headfile selected
            return cleaned_data
        headfiles = cleaned_data["headfiles"]

        for headfile in headfiles:
            for design_site in sites:
                if design_site in headfile.sites.all():
                    continue
                msg = _(
                    "Headfile %(headfile)r doesn't exist on site %(site)r!" % {
                        "headfile": headfile, "site": design_site
                    }
                )
                if "headfiles" in self._errors:
                    self._errors["headfiles"].append(msg)
                else:
                    self._errors["headfiles"] = self.error_class([msg])

        if "headfiles" in self._errors:
            # Remove non-valid field from the cleaned data
            del cleaned_data["headfiles"]

        colorscheme = cleaned_data["colorscheme"]
        for design_site in sites:
            if design_site in colorscheme.sites.all():
                continue

            msg = _(
                "Colorscheme %(colorscheme)r doesn't exist on site %(site)r!" % {
                    "colorscheme": colorscheme, "site": design_site
                }
            )
            self._errors["colorscheme"] = self.error_class([msg])

            # Remove non-valid field from the cleaned data
            del cleaned_data["colorscheme"]

        return cleaned_data


class DesignAdmin(VersionAdmin):
    form = DesignAdminForm
    list_display = ("id", "name", "template", "colorscheme", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    list_filter = ("sites", "template", "colorscheme", "createby", "lastupdateby")
    search_fields = ("name", "template", "colorscheme")

admin.site.register(models.Design, DesignAdmin)


#------------------------------------------------------------------------------


class EditableHtmlHeadFileAdminForm(forms.ModelForm):
    class Meta:
        model = models.EditableHtmlHeadFile

    def __init__(self, *args, **kwargs):
        super(EditableHtmlHeadFileAdminForm, self).__init__(*args, **kwargs)
        # Make mimetype optinal, so the user can leave to empty and auto_mimetype
        # would be used in model.clean_fields()
        self.fields["mimetype"].required = False

    def clean_sites(self):
        """
        Check if headfile sites contain the site from all design entries.
        """
        sites = self.cleaned_data["sites"]
        designs = models.Design.objects.all().filter(headfiles=self.instance)
        for design in designs:
            for design_site in design.sites.all():
                if design_site in sites:
                    continue
                raise forms.ValidationError(_(
                    "Headfile must exist on site %(site)r!"
                    " Because it's used by design %(design)r." % {
                        "site": design_site,
                        "design": design
                    }
                ))

        return sites

    def clean(self):
        """
        manually check a unique together, because django can't do this with a M2M field.
        Obsolete if unique_together work with ManyToMany: http://code.djangoproject.com/ticket/702
        
        Note:
        1. This can't be checked in model validation, because M2M fields
            are only accessible/updated after save()!
        2. In model pre_save signal is a unique together check, too.
        """
        cleaned_data = self.cleaned_data

        if "sites" not in cleaned_data or "filepath" not in cleaned_data:
            return cleaned_data

        filepath = cleaned_data["filepath"]
        sites = cleaned_data["sites"]

        headfiles = models.EditableHtmlHeadFile.objects.filter(filepath=filepath)
        if self.instance.id is not None:
            headfiles = headfiles.exclude(id=self.instance.id)

        for headfile in headfiles:
            for site in headfile.sites.all():
                if site not in sites:
                    continue

                if "filepath" not in self._errors:
                    self._errors["filepath"] = self.error_class([])

                self._errors["filepath"].append(_(
                    "EditableHtmlHeadFile with same filepath exist on site %r" % site
                ))

        if "filepath" in self._errors:
            # Remove non-valid field from the cleaned data
            del cleaned_data["filepath"]

        return cleaned_data

class EditableHtmlHeadFileAdmin(VersionAdmin):
    form = EditableHtmlHeadFileAdminForm
    list_display = ("id", "filepath", "site_info", "render", "description", "lastupdatetime", "lastupdateby")
    list_display_links = ("filepath", "description")
    list_filter = ("sites", "render")

admin.site.register(models.EditableHtmlHeadFile, EditableHtmlHeadFileAdmin)


#-----------------------------------------------------------------------------


class UserProfileAdmin(VersionAdmin):
    list_display = ("id", "user", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("user",)
    list_filter = ("sites",)

admin.site.register(models.UserProfile, UserProfileAdmin)



#-----------------------------------------------------------------------------
# Add ID to site admin by "reregister"
# FIXME: Is there a simpler way to do this?

class SiteAdmin(admin.ModelAdmin):
    list_display = ("id", 'domain', 'name')
    search_fields = ("id", 'domain', 'name')
    list_display_links = ("id", "domain")

admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)
