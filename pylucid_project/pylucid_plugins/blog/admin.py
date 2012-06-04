# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    :copyleft: 2008-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from django_tools.middlewares import ThreadLocal

# https://github.com/jedie/django-reversion-compare
from reversion_compare.admin import CompareVersionAdmin

from pylucid_project.apps.pylucid.base_admin import BaseAdmin
from pylucid_project.apps.pylucid.markup.admin import MarkupPreview
from pylucid_project.apps.pylucid.models.pluginpage import PluginPage
from pylucid_project.pylucid_plugins.blog.models import BlogEntry, \
    BlogEntryContent


class BlogBaseAdmin(BaseAdmin, CompareVersionAdmin):

    change_list_template = "reversion/blog/change_list.html"

    def __init__(self, *args, **kwargs):
        self.plugin_pages = PluginPage.objects.filter(app_label__endswith="blog")
        super(BlogBaseAdmin, self).__init__(*args, **kwargs)

    def changelist_view(self, request, extra_context=None):
        extra_context = {"plugin_pages":self.plugin_pages}
        return super(BlogBaseAdmin, self).changelist_view(request, extra_context=extra_context)


class BlogEntryAdmin(BlogBaseAdmin):
    """
    Language independend Blog entry.
    
    inherited attributes from BaseAdmin:
        view_on_site_link -> html link with the absolute uri.
    """
    def contents(self, obj):
        contents = BlogEntryContent.objects.filter(entry=obj)
        for entry in contents:
            entry.is_public_html = _boolean_icon(entry.is_public)
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
            # TODO: Create a link with the domain of the first site
            return u"<i>[not on current site]</i>"

        request = ThreadLocal.get_current_request()
        permalink = obj.get_permalink(request)
        if permalink is None:
            return u"<i>[no permalink available]</i>"

        context = {"permalink": permalink}
        html = render_to_string('admin/blog/permalink.html', context)
        return html
    permalink.allow_tags = True

    list_display = ("id", "is_public", "site_info", "contents", "permalink")
    list_filter = ("sites",)
admin.site.register(BlogEntry, BlogEntryAdmin)


class BlogEntryContentAdmin(BlogBaseAdmin, MarkupPreview):
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
