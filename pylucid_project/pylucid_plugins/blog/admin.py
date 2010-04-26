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

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin

from reversion.admin import VersionAdmin

from pylucid_project.apps.pylucid.base_admin import BaseAdmin

from blog.models import BlogEntry


class BlogEntryAdmin(BaseAdmin, VersionAdmin):
    """
    inherited attributes from BaseAdmin:
        view_on_site_link -> html link with the absolute uri.
    """
    list_display = ("id", "headline", "is_public", "view_on_site_link", "site_info", "lastupdatetime", "lastupdateby")
    list_display_links = ("headline",)
    list_filter = ("is_public", "sites", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("headline", "content")
    ordering = ('-lastupdatetime',)

admin.site.register(BlogEntry, BlogEntryAdmin)
