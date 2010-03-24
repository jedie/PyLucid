# coding: utf-8

"""
    PyLucid OpenStreetMap plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.utils.translation import ugettext_lazy as _

from reversion.admin import VersionAdmin

from pylucid_project.apps.pylucid_admin.admin_site import pylucid_admin_site

from OpenStreetMap.models import MapEntry


class MapEntryAdmin(VersionAdmin):
    def lucidTag_example(self, obj):
        return '{%% lucidTag OpenStreetMap name="%s" %%}' % obj.name

    lucidTag_example.short_description = _("lucidTag example")
    lucidTag_example.allow_tags = False

    list_display = ("name", "lucidTag_example", "lon", "lat", "marker_text")
    list_display_links = ("name",)
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("name", "marker_text")

pylucid_admin_site.register(MapEntry, MapEntryAdmin)
