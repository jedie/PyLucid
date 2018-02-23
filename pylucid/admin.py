# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2009-2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.core import serializers
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from cms.models import Page


logger = logging.getLogger(__name__)


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


# from djangocms_text_ckeditor.models import Text
# class TextAdmin(CompareVersionAdmin):
#     def placeholder_info(self, obj):
#         #Page.objects.filter(placeholders)
#         placeholder = obj.placeholder
#         plugins = placeholder.get_plugins()
#         plugin_ids_str = ",".join([str(plugin.pk) for plugin in plugins])
#         return "CMSPlugin: %s" % plugin_ids_str
#
#     placeholder_info.short_description = _("placeholder info")
#     # placeholder_info.allow_tags = True
#
#     list_display = ("id", "placeholder", "placeholder_info", "language", "plugin_type", "body")
#     list_filter = ("language",)
# admin.site.register(Text, TextAdmin)
