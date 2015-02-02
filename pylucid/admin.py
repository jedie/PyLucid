# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

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

logger = logging.getLogger(__name__)

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

from django.db.models.loading import get_app, get_apps, get_models
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered


def auto_register_all():
    """
    register all models with the admin interface.
    (Skip already registered models.)
    """
    for app in get_apps():
        for model in get_models(app):
            try:
                admin.site.register(model)
            except AlreadyRegistered:
                pass


def auto_patch_all():
    for app in get_apps():
        for model in get_models(app):
            try:
                patch_admin(model, skip_non_revision=True)
            except Exception as err:
                logging.warning("Can't patch admin for model %r: %s" % (model, err))


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

    auto_register_all()

    auto_patch_all()

