# coding: utf-8

from django.contrib import admin

from reversion.admin import VersionAdmin

from pylucid_admin import models


class PyLucidAdminPageAdmin(VersionAdmin):
    list_display = ("id", "name", "title", "url_name", "superuser_only", "access_permissions")
    list_display_links = ("name",)
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("name", "title", "url_name")

    def superuser_only(self, obj):
        superuser_only, access_permissions = obj.get_permissions()
        return superuser_only
    superuser_only.boolean = True

    def access_permissions(self, obj):
        superuser_only, access_permissions = obj.get_permissions()
        return " | ".join(access_permissions)

admin.site.register(models.PyLucidAdminPage, PyLucidAdminPageAdmin)
