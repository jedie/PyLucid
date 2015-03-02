# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db.models.loading import get_apps, get_models
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from cms.models import Page, Placeholder, CMSPlugin, Title

from reversion_compare.helpers import patch_admin

logger = logging.getLogger(__name__)




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


    class PlaceholderAdmin(admin.ModelAdmin):
        list_display = ("id", "slot", "default_width", "cache_placeholder", "is_static", "is_editable")
        list_filter = ("slot",)
    admin.site.register(Placeholder, PlaceholderAdmin)

    class CMSPluginAdmin(admin.ModelAdmin):
        list_display = ("id", "placeholder", "language", "plugin_type")
        list_filter = ("plugin_type","language")
    admin.site.register(CMSPlugin, CMSPluginAdmin)


    class TitleAdmin(admin.ModelAdmin):
        list_display = ("id", "language", "title", "page", "published", "publisher_is_draft", "publisher_public", "publisher_state")
        list_filter = ("language",)
    admin.site.register(Title, TitleAdmin)


    auto_register_all()

    auto_patch_all()