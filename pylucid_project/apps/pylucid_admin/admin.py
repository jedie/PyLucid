# coding: utf-8

from django.contrib import admin

from reversion.admin import VersionAdmin

from pylucid_admin import models


class PyLucidAdminPageAdmin(VersionAdmin):
    list_display = ("id", "name", "title", "url_name",)
    list_display_links = ("name",)
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("name", "title", "url_name")

admin.site.register(models.PyLucidAdminPage, PyLucidAdminPageAdmin)
