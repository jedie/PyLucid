# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    TODO:
        * if http://code.djangoproject.com/ticket/3400 is implement:
            Add site to list_filter for e.g. PageMeta, PageContent etc.
        * split this file
    
    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

from django import forms
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin, messages
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from reversion.admin import VersionAdmin

from dbtemplates.admin import TemplateAdmin, TemplateAdminForm
from dbtemplates.models import Template

from pylucid_project.apps.pylucid import models
from pylucid_project.apps.pylucid.base_admin import BaseAdmin
from pylucid_project.apps.pylucid.markup import hightlighter



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


if settings.DEBUG:
    class ColorAdmin(VersionAdmin):
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

    admin.site.register(models.Color, ColorAdmin)

class ColorInline(admin.TabularInline):
    model = models.Color
    extra = 0


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


class ColorSchemeAdmin(VersionAdmin):

    def clone(self, request, object_id):
        """ Clone a color scheme """
        colorscheme = models.ColorScheme.objects.get(id=object_id)
        sites = colorscheme.sites.all()
        old_name = colorscheme.name
        new_name = old_name + "_cloned"
    
        colors = models.Color.objects.filter(colorscheme=colorscheme)
    
        colorscheme.pk = None # make the object "new" ;)
        colorscheme.name = new_name
        colorscheme.save(force_insert=True)
        colorscheme.sites = sites
        colorscheme.save(force_update=True)
    
        for color in colors:
            color.pk = None # make the object "new" ;)
            color.colorscheme = colorscheme
            color.save(force_insert=True)
            color.sites = sites
            color.save(force_update=True)
    
        messages.success(request, 
            _("Colorscheme %(old_name)s cloned to %(new_name)s") % {
                "old_name": old_name, "new_name": new_name
            }
        )
        url = reverse("admin:pylucid_colorscheme_changelist")
        return HttpResponseRedirect(url)
    
    def get_urls(self):
        urls = super(ColorSchemeAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^(.+?)/clone/$', self.admin_site.admin_view(self.clone))
        )
        return my_urls + urls

#    def save_model(self, request, obj, form, change):
#        """ resave rendered headfiles """
#        print "ColorSchemeAdmin.save_model"
#        colorscheme = obj
#        colorscheme.save()


    def preview(self, obj):
        colors = models.Color.objects.all().filter(colorscheme=obj)
        context = {
            "colorscheme": obj,
            "colors": colors
        }
        return render_to_string("admin/pylucid/includes/colorscheme_preview.html", context)
    preview.short_description = 'color scheme preview'
    preview.allow_tags = True
    
    def design_usage_info(self, obj):
        designs = models.Design.objects.all().filter(colorscheme=obj)
        context = {"designs": designs}
        return render_to_string("admin/pylucid/includes/design_usage_info.html", context)
    design_usage_info.short_description = 'used in designs'
    design_usage_info.allow_tags = True
    
    form = ColorSchemeAdminForm
    list_display = ("id", "name", "preview", "design_usage_info", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("sites",)
    inlines = [ColorInline, ]

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
    def template_usage(self, obj):
        template_path = obj.template
        try:
            dbtemplate_entry = Template.objects.get(name=template_path)
        except Template.DoesNotExist:
            dbtemplate_entry = None
        
        context = {
            "design": obj,
            "dbtemplate_entry":dbtemplate_entry,
        }
        return render_to_string("admin/pylucid/design_template_info.html", context)
    
    template_usage.short_description = 'Template'
    template_usage.allow_tags = True
    
    def color_info(self, obj):
        colorscheme = obj.colorscheme
        colors = models.Color.objects.all().filter(colorscheme=colorscheme)
        context = {
            "add_colorscheme_name": True,
            "colorscheme": colorscheme,
            "colors": colors
        }
        return render_to_string("admin/pylucid/includes/colorscheme_preview.html", context)
    color_info.short_description = 'color scheme information'
    color_info.allow_tags = True
    
    def headfiles_info(self, obj):
        colorscheme = obj.colorscheme
        colors = models.Color.objects.all().filter(colorscheme=colorscheme)
        headfiles = obj.headfiles.all()
        for headfile in headfiles:
            headfile.absolute_url = headfile.get_absolute_url(colorscheme)
            
        context = {
            "design": obj,
            "headfiles": headfiles,
            "colorscheme": obj.colorscheme,
            "colors": colors,
        }
        return render_to_string("admin/pylucid/design_headfiles_info.html", context)
    
    headfiles_info.short_description = 'used headfiles'
    headfiles_info.allow_tags = True
    
    form = DesignAdminForm
    list_display = ("id", "name", "template_usage", "color_info", "headfiles_info", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    list_filter = ("sites", "template", "colorscheme", "createby", "lastupdateby")
    search_fields = ("name", "template", "colorscheme")

admin.site.register(models.Design, DesignAdmin)


#------------------------------------------------------------------------------


class EditableHtmlHeadFileAdminForm(forms.ModelForm):
    class Meta:
        model = models.EditableHtmlHeadFile
    class Media:
        js = (
            settings.MEDIA_URL + "PyLucid/codemirror_editable_headfile.js",
        )

    def __init__(self, *args, **kwargs):
        super(EditableHtmlHeadFileAdminForm, self).__init__(*args, **kwargs)
        # Make mimetype optinal, so the user can leave to empty and auto_mimetype
        # would be used in model.clean_fields()
        self.fields["mimetype"].required = False

        # Don't apply jquery.textarearesizer.js:
        self.fields["content"].widget.attrs["class"] += " processed"

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


#-----------------------------------------------------------------------------
# Use own ColorMirror editor in dbtemplates

class DBTemplatesAdminAdminForm(TemplateAdminForm):
    class Media:
        js = (settings.MEDIA_URL + "PyLucid/codemirror_dbtemplates.js",)

    def __init__(self, *args, **kwargs):
        super(DBTemplatesAdminAdminForm, self).__init__(*args, **kwargs)
        # Don't apply jquery.textarearesizer.js:
        self.fields["content"].widget.attrs["class"] = " processed"



class DBTemplatesAdmin(TemplateAdmin):  
    def _filesystem_template_path(self, template_name):
        """ return absolute filesystem path to given template name """
        for dir in settings.TEMPLATE_DIRS:
            abs_path = os.path.join(dir, template_name)
            if os.path.isfile(abs_path):
                return abs_path
    
    def _get_filesystem_template(self, template_path):
        """ return template content from filesystem """
        f = file(template_path, "r")
        content = f.read()
        f.close()
        return content

    def diff_view(self, request, object_id):
        """
        AJAX view to display a diff between current edited content
        and the template content from filesystem, if found.
        """
        if request.is_ajax() != True or request.method != 'POST' or "content" not in request.POST:
            return HttpResponse("ERROR: Wrong request")

        edit_content = request.POST["content"]
       
        try:
            dbtemplate_obj = Template.objects.only("name").get(id=object_id)
        except Template.DoesNotExist, err:
            msg = "Template with ID %r doesn't exist!" % object_id
            return HttpResponse(msg)
        
        templatename = dbtemplate_obj.name
        
        template_path = self._filesystem_template_path(templatename)
        if template_path is None:
            msg = "Error: Template %r not found on filesystem." % templatename
            return HttpResponse(msg)
        
        try:
            filesystem_template = self._get_filesystem_template(template_path)
        except Exception, err:
            msg = "Error: Can't read %r: %s" % (template_path, err)
            return HttpResponse(msg)
             
        diff_html = hightlighter.get_pygmentize_diff(filesystem_template, edit_content)
        
        return HttpResponse(diff_html)

    def get_urls(self):
        """Returns the additional urls."""
        urls = super(DBTemplatesAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name,
        new_urls = patterns("",
            url("^(.+)/diff/$", admin_site.admin_view(self.diff_view), name='%s_%s_diff' % info),
        )
        return new_urls + urls
    
    def usage_info(self, obj):
        designs = models.Design.objects.all().filter(template=obj.name)
        
        context = {
            "designs": designs,
        }
        return render_to_string("admin/pylucid/dbtemplate_usage_info.html", context)
    
    usage_info.short_description = 'used in PyLucid design'
    usage_info.allow_tags = True

    form = DBTemplatesAdminAdminForm
    list_display = ('name', "usage_info", 'creation_date', 'last_changed', 'site_list')

admin.site.unregister(Template)
admin.site.register(Template, DBTemplatesAdmin)