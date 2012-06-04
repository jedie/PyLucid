# coding: utf-8

"""
    PyLucid StreetMap plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~


    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-reversion-compare
from reversion_compare.admin import CompareVersionAdmin

from StreetMap.models import MapEntry



class MapEntryAdmin(CompareVersionAdmin):
    def lucidTag_example(self, obj):
        return '{%% lucidTag StreetMap name="%s" %%}' % obj.name
    lucidTag_example.short_description = _("lucidTag example")
    
    def preview(self, obj):
        map_type = obj.map_type
        template_name = MapEntry.LINK_TEMPLATE[map_type]
        return render_to_string(template_name, {"map":obj})
    preview.short_description = _("preview")
    preview.allow_tags = True

    list_display = ("name", "lucidTag_example", "preview", "lon", "lat", "marker_text")
    list_display_links = ("name",)
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("name", "marker_text")

admin.site.register(MapEntry, MapEntryAdmin)
