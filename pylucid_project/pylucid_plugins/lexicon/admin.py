# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register models in django admin interface.

    :copyleft: 2008-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin

# https://github.com/jedie/django-reversion-compare
from reversion_compare.admin import CompareVersionAdmin

from pylucid_project.apps.pylucid.base_admin import BaseAdmin
from pylucid_project.apps.pylucid.markup.admin import MarkupPreview

from lexicon.models import LexiconEntry


class LexiconEntryAdmin(BaseAdmin, MarkupPreview, CompareVersionAdmin):
    """
    inherited attributes from BaseAdmin:
        view_on_site_link -> html link with the absolute uri.
        
    inherited from MarkupPreview:
        ajax_markup_preview() -> the markup content ajax preview view
        get_urls()            -> add ajax view to admin urls 
    """
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
