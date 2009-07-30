# coding: utf-8

from django.contrib import admin
from pylucid_admin.admin import pylucid_admin_site

from pylucid_comments.models import PyLucidComment

class PyLucidCommentAdmin(admin.ModelAdmin):
    pass
#    list_display = ("id", "headline", "is_public", "get_absolute_url", "lastupdatetime", "lastupdateby")
#    list_display_links = ("headline",)
#    list_filter = ("is_public", "createby", "lastupdateby",)
#    date_hierarchy = 'lastupdatetime'
#    search_fields = ("headline", "content")

pylucid_admin_site.register(PyLucidComment, PyLucidCommentAdmin)
