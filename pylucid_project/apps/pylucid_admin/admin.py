# coding: utf-8

from django.contrib import admin

from reversion.admin import VersionAdmin

from pylucid_admin import models


class PyLucidAdminPageAdmin(VersionAdmin):
    list_display = ("id", "name", "title", "url_name", "superuser_only", "display_access_permissions")
    list_display_links = ("name",)
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("name", "title", "url_name")
    def display_access_permissions(self, obj):
        obj.access_permissions
        permissions = obj.access_permissions.select_related()
        return " | ".join([u"%s.%s" % (p.content_type.app_label, p.codename) for p in permissions])

admin.site.register(models.PyLucidAdminPage, PyLucidAdminPageAdmin)
