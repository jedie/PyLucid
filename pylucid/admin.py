# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response

from reversion.admin import VersionAdmin

from cms.models.pagemodel import Page

from reversion_compare.helpers import patch_admin


# Patch django-cms Page Model to add reversion-compare functionality:
patch_admin(Page)



def export_as_json(modeladmin, request, queryset):
    """
    from:
    http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages
    """
    response = HttpResponse(content_type="text/javascript")
    serializers.serialize("json", queryset, stream=response, indent=4)
    return response

# Make export actions available site-wide
admin.site.add_action(export_as_json, 'export_selected_as_json')


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

