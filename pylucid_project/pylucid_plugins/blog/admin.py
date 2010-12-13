# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls.defaults import patterns, url
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Permission

from reversion.admin import VersionAdmin

from pylucid_project.apps.pylucid.base_admin import BaseAdmin

from blog.models import BlogEntry


from pylucid_project.apps.pylucid.markup.forms_utils import MarkupContentWidget, \
    MarkupPreview





class BlogEntryAdminForm(forms.ModelForm):
    class Meta:
        model = BlogEntry

    def __init__(self, *args, **kwargs):
        super(BlogEntryAdminForm, self).__init__(*args, **kwargs)

        self.fields["content"].widget = MarkupContentWidget()


class BlogEntryAdmin(BaseAdmin, VersionAdmin, MarkupPreview):
    """
    inherited attributes from BaseAdmin:
        view_on_site_link -> html link with the absolute uri.
    """
    template = "blog/new_blog_entry.html"
    save_on_top = True
    form = BlogEntryAdminForm
    list_display = ("id", "headline", "is_public", "view_on_site_link", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("headline",)
    list_filter = ("is_public", "sites", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("headline", "content")
    ordering = ('-lastupdatetime',)

    def get_urls(self):
        urls = super(BlogEntryAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^(.+?)/preview/$', self.admin_site.admin_view(self.ajax_preview)),
        )
        return my_urls + urls

admin.site.register(BlogEntry, BlogEntryAdmin)
