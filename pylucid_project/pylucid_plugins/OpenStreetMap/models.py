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

from django.db import models
from django.core import urlresolvers
from django.db.models import signals
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal

from pylucid_project.apps.pylucid.models import PageContent
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.models.base_models import AutoSiteM2M, UpdateInfoBaseModel

class MapEntry(AutoSiteM2M, UpdateInfoBaseModel):
    name = models.SlugField(help_text=_("Short name for lucidTag"))
    
    width = models.PositiveIntegerField(
        default=450,
        help_text=_("Map width size")
    )
    height = models.PositiveIntegerField(
        default=350,
        help_text=_("Map height size")
    )
    
    # http://www.openstreetmap.org/?lat=51.430123&lon=6.774099&zoom=18&layers=B000FTF
    lon = models.FloatField(
        help_text=_("map geographic longitude (vertically) coordinate"),
    )
    lat = models.FloatField(
        help_text=_("map geographic latitude (horizontally) coordinate"),
    )
    zoom = models.PositiveSmallIntegerField(
        default=12,
        help_text=_("Map zoom factor"),
    )
    
    marker_lon = models.FloatField(
        help_text=_("Text marker longitude (vertically) coordinate")
    )
    marker_lat = models.FloatField(
        help_text=_("Text marker latitude (horizontally) coordinate")
    )
    marker_width = models.PositiveIntegerField(
        default=180,
        help_text=_("Text marker width size")
    )
    marker_height = models.PositiveIntegerField(
        default=125,
        help_text=_("Text marker height size")
    )
    marker_text=models.TextField(help_text=_("Marker text"))
    markup = models.IntegerField(max_length=1,
        default=PageContent.MARKUP_CREOLE,
        choices=PageContent.MARKUP_CHOICES
    )
    
    def get_html(self):
        """ return the marker_text as html """
        request = ThreadLocal.get_current_request()
        html = apply_markup(
            raw_content=self.marker_text,
            markup_no=self.markup, 
            page_msg=request.page_msg
        )
        # Needed for JavaScript:
        html = html.strip().replace("\n", "").replace('"', '\"')
        return mark_safe(html)