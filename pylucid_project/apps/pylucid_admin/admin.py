# coding: utf-8

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response

from reversion.admin import VersionAdmin

from pylucid_project.apps.pylucid_admin import models


#-----------------------------------------------------------------------------
# some django admin stuff is broken if TEMPLATE_STRING_IF_INVALID != ""
# http://code.djangoproject.com/ticket/3579

if settings.TEMPLATE_STRING_IF_INVALID != "":
    # Patch the render_to_response function ;)
    from django.contrib.auth import admin as auth_admin
    from django.contrib.admin import options

    def patched_render_to_response(*args, **kwargs):
        old = settings.TEMPLATE_STRING_IF_INVALID
        settings.TEMPLATE_STRING_IF_INVALID = ""
        result = render_to_response(*args, **kwargs)
        settings.TEMPLATE_STRING_IF_INVALID = old
        return result

    options.render_to_response = patched_render_to_response
    auth_admin.render_to_response = patched_render_to_response


#-----------------------------------------------------------------------------


def export_as_json(modeladmin, request, queryset):
    """
    from:
    http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages
    """
    response = HttpResponse(mimetype="text/javascript")
    serializers.serialize("json", queryset, stream=response, indent=4)
    return response

# Make export actions available site-wide
admin.site.add_action(export_as_json, 'export_selected_as_json')


#-----------------------------------------------------------------------------


if settings.DEBUG:
    class PermissionAdmin(admin.ModelAdmin):
        """ django auth Permission """
        list_display = ("id", "name", "content_type", "codename")
        list_display_links = ("name", "codename")
        list_filter = ("content_type",)
    admin.site.register(Permission, PermissionAdmin)

    class ContentTypeAdmin(admin.ModelAdmin):
        """ django ContentType """
        list_display = list_display_links = ("id", "app_label", "name", "model")
        list_filter = ("app_label",)
    admin.site.register(ContentType, ContentTypeAdmin)

    #-----------------------------------------------------------------------------

    from reversion.models import Revision, Version

    class RevisionAdmin(admin.ModelAdmin):
        list_display = ("id", "date_created", "user", "comment")
        list_display_links = ("date_created",)
        date_hierarchy = 'date_created'
        ordering = ('-date_created',)
        list_filter = ("user", "comment")
        search_fields = ("user", "comment")

    admin.site.register(Revision, RevisionAdmin)


    class VersionAdmin(admin.ModelAdmin):
        list_display = ("object_repr", "revision", "object_id", "content_type", "format",)
        list_display_links = ("object_repr", "object_id")
        list_filter = ("content_type", "format")
        search_fields = ("object_repr", "serialized_data")

    admin.site.register(Version, VersionAdmin)

    #-----------------------------------------------------------------------------

    class PyLucidAdminPageAdmin(VersionAdmin):
        list_display = (
            "id", "name", "get_absolute_url",
            "superuser_only", "must_staff", "permissions",
            "get_pagetree", "get_pagemeta", "get_page",
        )
        list_display_links = ("name",)
        list_filter = ("createby", "lastupdateby",)
        date_hierarchy = 'lastupdatetime'
        search_fields = ("name", "title", "url_name")

        def superuser_only(self, obj):
            access_permissions = obj.get_permissions()
            superuser_only, permissions, must_staff = access_permissions
            return superuser_only
        superuser_only.boolean = True

        def must_staff(self, obj):
            access_permissions = obj.get_permissions()
            superuser_only, permissions, must_staff = access_permissions
            return must_staff
        must_staff.boolean = True

        def permissions(self, obj):
            access_permissions = obj.get_permissions()
            superuser_only, permissions, must_staff = access_permissions
            return "<br />".join(permissions)
        permissions.allow_tags = True

    admin.site.register(models.PyLucidAdminPage, PyLucidAdminPageAdmin)
