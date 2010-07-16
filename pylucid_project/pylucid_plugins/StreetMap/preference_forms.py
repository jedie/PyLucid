# coding: utf-8


from django import forms
from django.utils.translation import ugettext as _

from dbpreferences.forms import DBPreferencesBaseForm

class PreferencesForm(DBPreferencesBaseForm):
    google_maps_api_key = forms.CharField(
        initial="",required=False,
        help_text=_("Google Maps API Key (Leave empty if you only use OpenStreetMaps.)")
    )

    class Meta:
        app_label = 'StreetMap'
