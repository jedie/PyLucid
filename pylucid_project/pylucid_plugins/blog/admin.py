# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    :copyleft: 2008-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from reversion.admin import VersionAdmin

from django_tools.middlewares import ThreadLocal

from pylucid_project.apps.pylucid.base_admin import BaseAdmin
from pylucid_project.apps.pylucid.markup.admin import MarkupPreview
from pylucid_project.pylucid_plugins.blog.models import BlogEntry, \
    BlogEntryContent
import traceback



class BlogEntryAdmin(BaseAdmin):
    """
    Language independend Blog entry.
    
    inherited attributes from BaseAdmin:
        view_on_site_link -> html link with the absolute uri.
    """
    def contents(self, obj):
        contents = BlogEntryContent.objects.filter(entry=obj)
        context = {
            "contents": contents
        }
        return render_to_string("admin/blog/entry_contents.html", context)
    contents.short_description = _("Edit existing content entries")
    contents.allow_tags = True

    def permalink(self, obj):
        """ view on site link in admin changelist, try to use complete uri with site info. """
        current_site = Site.objects.get_current()

        count = obj.sites.filter(id=current_site.id).count()
        if count == 0:
            return u"<i>[not on current site]</i>"

        request = ThreadLocal.get_current_request()
        permalink = obj.get_permalink(request)
        if permalink is None:
            return u"<i>[no permalink available]</i>"

        context = {"permalink": permalink}
        html = render_to_string('admin/blog/permalink.html', context)
        return html

    permalink.allow_tags = True

    list_display = ("id", "site_info", "contents", "permalink")
    list_filter = ("sites",)
admin.site.register(BlogEntry, BlogEntryAdmin)


class BlogEntryContentAdmin(BaseAdmin, MarkupPreview, VersionAdmin):
    """
    Language depend blog entry content.
    
    inherited attributes from BaseAdmin:
        view_on_site_link -> html link with the absolute uri.
        
    inherited from MarkupPreview:
        ajax_markup_preview() -> the markup content ajax preview view
        get_urls()            -> add ajax view to admin urls 
    """
    list_display = ("id", "headline", "is_public", "view_on_site_link", "lastupdatetime", "lastupdateby", "createtime")
    list_display_links = ("headline",)
    list_filter = ("is_public", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("headline", "content")
    ordering = ('-lastupdatetime',)

admin.site.register(BlogEntryContent, BlogEntryContentAdmin)
