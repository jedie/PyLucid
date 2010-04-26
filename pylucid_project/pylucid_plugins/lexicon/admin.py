# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register models in django admin interface.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin

from reversion.admin import VersionAdmin

from pylucid_project.apps.pylucid.base_admin import BaseAdmin

from lexicon.models import LexiconEntry


class LexiconEntryAdmin(BaseAdmin, VersionAdmin):
    list_display = (
        "id", "term", "language", "tags", "is_public",
        "view_on_site_link", "site_info",
        "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("term", "tags",)
    list_filter = ("is_public", "language", "sites", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    ordering = ('-lastupdatetime',)
    search_fields = ("term", "tags", "content")

admin.site.register(LexiconEntry, LexiconEntryAdmin)
