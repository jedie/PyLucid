# coding: utf-8

from django.db import models
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.comments.models import Comment

from pylucid_admin.admin import pylucid_admin_site

from pylucid.models import PageContent, Language



class PyLucidComment(Comment):
    title = models.CharField(max_length=300)
    lang = models.ForeignKey(Language)





class PyLucidCommentAdmin(admin.ModelAdmin):
    pass
#    list_display = ("id", "headline", "is_public", "get_absolute_url", "lastupdatetime", "lastupdateby")
#    list_display_links = ("headline",)
#    list_filter = ("is_public", "createby", "lastupdateby",)
#    date_hierarchy = 'lastupdatetime'
#    search_fields = ("headline", "content")

try:
    pylucid_admin_site.register(PyLucidComment, PyLucidCommentAdmin)
except AlreadyRegistered:
    pass # FIXME
