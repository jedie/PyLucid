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

__version__ = "$Rev:$"

from django.conf import settings
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import render_to

from OpenStreetMap.models import MapEntry


@render_to("OpenStreetMap/OpenStreetMap.html")
def lucidTag(request, name=None):
    """
    Display a map inline.
    First create a map entry in django admin panel.
    Then use the name for the lucidTag parameter.
    
    example:
        {% lucidTag OpenStreetMap name="MyMapName" %}
    """
    if name is None:
        if settings.DEBUG or request.user.is_staff:
            request.page_msg.error(_("lucidTag OpenStreetMap error: You must add the 'name' parameter!"))
        return "[OpenStreetMap Error]"
    
    try:
        map_entry = MapEntry.objects.get(name=name)
    except MapEntry.DoesNotExist:
        if settings.DEBUG or request.user.is_staff:
            request.page_msg.error(
                _("lucidTag OpenStreetMap error:"
                  " There exist no map entry with the name: %r") % name
            )
            existing_names = MapEntry.objects.values_list('name', flat=True)
            request.page_msg(_("Existing maps are: %r") % existing_names)
        return "[OpenStreetMap Error]"
    
    context = {
        "map":map_entry,
        "lang_code": request.PYLUCID.current_language.code, 
    }
    return context