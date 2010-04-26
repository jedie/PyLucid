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

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin

from update_journal.models import UpdateJournal, PageUpdateListObjects


class UpdateJournalAdmin(admin.ModelAdmin):
    list_display = ("id", "lastupdatetime", "user_name", "content_type", "object_url", "language", "title", "staff_only")
    list_display_links = ("object_url",)
    list_filter = ("user_name", "content_type", "staff_only")
#    date_hierarchy = 'lastupdatetime'
#    search_fields = ("headline", "content")

admin.site.register(UpdateJournal, UpdateJournalAdmin)

#class PageUpdateListObjectsAdmin(admin.ModelAdmin):
#    list_display = ("id", "content_type", "staff_only")
#    list_display_links = ("content_type",)
#    list_filter = ("content_type", "staff_only")
#
#admin.site.register(PageUpdateListObjects, PageUpdateListObjectsAdmin)
