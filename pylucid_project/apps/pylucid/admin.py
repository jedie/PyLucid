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
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.admin.util import unquote
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-reversion-compare
from reversion_compare.admin import CompareVersionAdmin

from dbtemplates.admin import TemplateAdmin, TemplateAdminForm
from dbtemplates.models import Template

from pylucid_project.apps.pylucid import models
from pylucid_project.apps.pylucid.base_admin import BaseAdmin
from pylucid_project.apps.pylucid.forms.pagemeta import PageMetaForm
from pylucid_project.apps.pylucid.markup import hightlighter
from pylucid_project.apps.pylucid.markup.admin import MarkupPreview
from django.shortcuts import render_to_response
from pylucid_project.apps.pylucid.decorators import render_to
from django.template.context import RequestContext


class PageTreeAdmin(BaseAdmin, CompareVersionAdmin):
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

admin.site.register(models.PageTree, PageTreeAdmin)


class BanEntryAdmin(admin.ModelAdmin):
    list_display = list_display_links = ("ip_address", "createtime",)
    search_fields = ("ip_address",)
admin.site.register(models.BanEntry, BanEntryAdmin)


class LanguageAdmin(CompareVersionAdmin):
    list_display = ("code", "description", "site_info", "permitViewGroup")
    list_display_links = ("code", "description")
    list_filter = ("permitViewGroup",)
admin.site.register(models.Language, LanguageAdmin)


class LogEntryAdmin(BaseAdmin):
    def age(self, obj):
        """ view on site link in admin changelist, try to use complete uri with site info. """
        createtime = obj.createtime
        return timesince(createtime)

    age.short_description = _("age")

    list_display = (
        "createtime", "age", "createby", "view_on_site_link", "app_label", "action", "message"
    )
    list_filter = (
        "site", "app_label", "action", "createby", "remote_addr",
    )
    search_fields = ("app_label", "action", "message", "long_message", "data")
admin.site.register(models.LogEntry, LogEntryAdmin)


#class OnSitePageMeta(models.PageMeta):
#    def get_site(self):
#        return self.page.site
#    site = property(get_site)
#    class Meta:
#        proxy = True



class PageMetaAdmin(BaseAdmin, CompareVersionAdmin):
    form = PageMetaForm
    list_display = ("id", "get_title", "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",)
    list_display_links = ("id", "get_title")
    list_filter = ("language", "createby", "lastupdateby", "tags")#"keywords"
    date_hierarchy = 'lastupdatetime'
    search_fields = ("description", "keywords")

admin.site.register(models.PageMeta, PageMetaAdmin)


class PageContentInline(admin.StackedInline):
    model = models.PageContent

class PageContentAdmin(BaseAdmin, MarkupPreview, CompareVersionAdmin):
    """
    inherited attributes from BaseAdmin:
        view_on_site_link -> html link with the absolute uri.
        
    inherited from MarkupPreview:
        ajax_markup_preview() -> the markup content ajax preview view
        get_urls()            -> add ajax view to admin urls 
    """
    list_display = ("id", "get_title", "get_site", "view_on_site_link", "lastupdatetime", "lastupdateby",)
    list_display_links = ("id", "get_title")
    list_filter = ("markup", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("content",) # it would be great if we can add "get_title"

admin.site.register(models.PageContent, PageContentAdmin)


class PluginPageAdmin(BaseAdmin, CompareVersionAdmin):
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

admin.site.register(models.Color, ColorAdmin)

class ColorInline(admin.TabularInline):
    model = models.Color
    extra = 0


class ColorSchemeAdmin(CompareVersionAdmin):

    def clone(self, request, object_id):
        """ Clone a color scheme """
        colorscheme = models.ColorScheme.objects.get(id=object_id)
        old_name = colorscheme.name
        new_name = old_name + "_cloned"

        colors = models.Color.objects.filter(colorscheme=colorscheme)

        colorscheme.pk = None # make the object "new" ;)
        colorscheme.name = new_name
        colorscheme.save(force_insert=True)

        for color in colors:
            color.pk = None # make the object "new" ;)
            color.colorscheme = colorscheme
            color.save(force_insert=True)

        messages.success(request,
            _("Colorscheme %(old_name)s cloned to %(new_name)s") % {
                "old_name": old_name, "new_name": new_name
            }
        )
        url = reverse("admin:pylucid_colorscheme_changelist")
        return HttpResponseRedirect(url)

    def cleanup(self, request, object_id):
        """ remove all unused colors """

        colorscheme = models.ColorScheme.objects.get(id=object_id)
        colorscheme.cleanup(request)

        url = reverse("admin:pylucid_colorscheme_change", args=(object_id,))
        return HttpResponseRedirect(url)

    def get_urls(self):
        urls = super(ColorSchemeAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^(.+?)/clone/$', self.admin_site.admin_view(self.clone)),
            (r'^(.+?)/cleanup/$', self.admin_site.admin_view(self.cleanup)),
        )
        return my_urls + urls

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

    change_list_template = "admin/pylucid/change_list_with_design_link.html"
    list_display = ("id", "name", "preview", "design_usage_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = [ColorInline, ]

admin.site.register(models.ColorScheme, ColorSchemeAdmin)


#------------------------------------------------------------------------------


class DesignAdminForm(forms.ModelForm):
    class Meta:
        model = models.Design

    def clean(self):
        """ Check if all pages exist on the site. """
        cleaned_data = self.cleaned_data

        if "sites" in cleaned_data:
            sites = cleaned_data["sites"]
            queryset = models.PageTree.objects.all().filter(design=self.instance).exclude(site__in=sites)
            page_count = queryset.count()
            if page_count > 0:
                site = queryset[0].site
                msg = _("Error: At least %(count)s page(s) used this design on site %(site)s!") % {
                    "count": page_count, "site": site
                }
                self._errors["sites"] = self.error_class([msg])

        return cleaned_data


class DesignAdmin(CompareVersionAdmin):
    def page_count(self, obj):
        queryset = models.PageTree.objects.all().filter(design=obj)
        count = queryset.count()
        if count > 0:
            first_page = queryset[0]
        else:
            first_page = None

        context = {
            "design": obj,
            "count":count,
            "first_page": first_page,
        }
        return render_to_string("admin/pylucid/design_page_count.html", context)

    page_count.short_description = 'page count'
    page_count.allow_tags = True

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
    template_usage.admin_order_field = "template"

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
    color_info.admin_order_field = "colorscheme"

    def headfiles_info(self, obj):
        colorscheme = obj.colorscheme
        colors = models.Color.objects.all().filter(colorscheme=colorscheme)
        headfiles = obj.headfiles.all()
        for headfile in headfiles:
            if headfile.render:
                headfile.absolute_url = headfile.get_absolute_url(colorscheme)
            else:
                headfile.absolute_url = headfile.get_absolute_url()

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
    list_display = ("id", "name", "page_count", "template_usage", "color_info", "headfiles_info", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("name",)
    ordering = ("name",)
    list_filter = ("sites", "template", "colorscheme", "createby", "lastupdateby")
    search_fields = ("name", "template", "colorscheme")

admin.site.register(models.Design, DesignAdmin)


#------------------------------------------------------------------------------


class EditableHtmlHeadFileAdminForm(forms.ModelForm):
    class Meta:
        model = models.EditableHtmlHeadFile
    class Media:
        js = (
            settings.STATIC_URL + "PyLucid/codemirror_editable_headfile.js",
        )

    def __init__(self, *args, **kwargs):
        super(EditableHtmlHeadFileAdminForm, self).__init__(*args, **kwargs)
        # Make mimetype optinal, so the user can leave to empty and auto_mimetype
        # would be used in model.clean_fields()
        self.fields["mimetype"].required = False


class EditableHtmlHeadFileAdmin(CompareVersionAdmin):
    form = EditableHtmlHeadFileAdminForm
    change_list_template = "admin/pylucid/change_list_with_design_link.html"
    list_display = ("id", "filepath", "render", "description", "lastupdatetime", "lastupdateby")
    list_display_links = ("filepath", "description")
    list_filter = ("render",)

admin.site.register(models.EditableHtmlHeadFile, EditableHtmlHeadFileAdmin)


#-----------------------------------------------------------------------------


class UserProfileAdmin(CompareVersionAdmin):
    class SiteForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        sites = forms.ModelMultipleChoiceField(Site.objects)

    def set_site(self, request, queryset):
        if "cancel" in request.POST:
            # User has clicked on the cancel form submit button
            self.message_user(request, "Cancelled 'set site'")
            return HttpResponseRedirect(request.get_full_path())

        if "save" in request.POST:
            form = self.SiteForm(request.POST)
            if form.is_valid():
                sites = form.cleaned_data["sites"]
                count = 0
                for userprofile in queryset:
                    userprofile.sites = sites
                    userprofile.save()
                    count += 1
                self.message_user(request, _("Saved sites to %i userprofiles." % count))
                return HttpResponseRedirect(request.get_full_path())
        else:
            selected_action = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
            form = self.SiteForm(initial={"_selected_action": selected_action})

        context = {
            "queryset": queryset,
            "form": form,
            "abort_url": request.get_full_path(),
            "form_url":request.get_full_path(),
        }
        return render_to_response("admin/set_user_sites.html", context, context_instance=RequestContext(request))

    set_site.short_description = "Change the site for selected users."

    list_display = ("id", "user", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("user",)
    list_filter = ("sites",)
    actions = ["set_site"]

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
# Use CompareVersionAdmin and own ColorMirror editor in dbtemplates

class DBTemplatesAdminAdminForm(TemplateAdminForm):
    class Media:
        js = (settings.STATIC_URL + "PyLucid/codemirror_dbtemplates.js",)

#    def __init__(self, *args, **kwargs):
#        super(DBTemplatesAdminAdminForm, self).__init__(*args, **kwargs)



class DBTemplatesAdmin(CompareVersionAdmin, TemplateAdmin):
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
    change_list_template = "admin/pylucid/change_list_with_design_link.html"
    list_display = ('name', "usage_info", 'creation_date', 'last_changed', 'site_list')
    ordering = ("-last_changed",)

try:
    admin.site.unregister(Template)
except NotRegistered, err:
    pass
admin.site.register(Template, DBTemplatesAdmin)
