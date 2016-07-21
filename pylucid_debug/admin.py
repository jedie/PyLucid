# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015-2016 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from cms.models import Page, Placeholder, CMSPlugin, Title

from reversion_compare.helpers import patch_admin
from pylucid_migration.models import PageProxyModel

logger = logging.getLogger(__name__)


SKIP_MODELS=(
    "Alias", # multisite.models.Alias
)

def iter_models():
    app_configs = apps.get_app_configs()
    for app_config in app_configs:
        models = app_config.get_models()
        for model in models:
            yield model


def auto_register_all():
    """
    register all models with the admin interface.
    (Skip already registered models.)
    """
    for model in iter_models():
        if model.__name__ in SKIP_MODELS:
            continue
        try:
            admin.site.register(model)
            # print("Register model %s in admin via 'pylucid_debug' app." % model)
        except AlreadyRegistered:
            pass


def auto_patch_all():
    for model in iter_models():
        if model.__name__ in SKIP_MODELS:
            continue
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


    class PageLowLevelAdmin(admin.ModelAdmin):
        def url(self, obj):
            return obj.get_absolute_url()

        def title(self, obj):
            return obj

        def template_info(self, obj):
            return "<br />".join([
                obj.template,
                obj.get_template(),
                obj.get_template_name(),
            ])
        template_info.allow_tags = True

        def ancestors(self, obj):
            ancestors = obj.get_ancestors(ascending=True)
            return "<br />".join([ancestor.get_absolute_url() for ancestor in ancestors])
        ancestors.allow_tags=True

        list_display = ("url", "title", "publisher_is_draft", "created_by", "creation_date", "changed_by", "changed_date", "template_info", "ancestors", "site")
        list_display_links = ("url", "title")
        list_filter = ("publisher_is_draft", "created_by", "changed_by", "site")

    admin.site.register(PageProxyModel, PageLowLevelAdmin)

    auto_register_all()

    auto_patch_all()