# coding: utf-8

"""
    PyLucid StreetMap plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import render_to

from StreetMap.models import MapEntry
from StreetMap.preference_forms import PreferencesForm

@render_to()
def lucidTag(request, name=None):
    """
    Display a map inline.
    First create a map entry in django admin panel.
    Then use the name for the lucidTag parameter.
    
    example:
        {% lucidTag StreetMap name="MyMapName" %}
    """
    if name is None:
        if settings.DEBUG or request.user.is_staff:
            messages.error(request, _("lucidTag StreetMap error: You must add the 'name' parameter!"))
        return "[StreetMap Error]"

    try:
        map_entry = MapEntry.objects.get(name=name)
    except MapEntry.DoesNotExist:
        if settings.DEBUG or request.user.is_staff:
            messages.error(request,
                _("lucidTag StreetMap error:"
                  " There exist no map entry with the name: %r") % name
            )
            existing_names = MapEntry.objects.values_list('name', flat=True)
            messages.info(request, _("Existing maps are: %r") % existing_names)
        return "[StreetMap Error]"
    
    if settings.DEBUG or request.user.is_staff:
        map_entry.check_google_api_key()

    # Get preferences from DB
    pref_form = PreferencesForm()
    preferences = pref_form.get_preferences()

    context = {
        "google_maps_api_key": preferences["google_maps_api_key"],
        "map":map_entry,
        "marker_lon": map_entry.marker_lon or map_entry.lon,
        "marker_lat": map_entry.marker_lat or map_entry.lat,
        "marker_html": map_entry.get_html(),
        "template_name": map_entry.get_template_name(),
        "lang_code": request.PYLUCID.current_language.code,
    }
    return context
