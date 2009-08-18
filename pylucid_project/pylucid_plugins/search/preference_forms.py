# coding: utf-8


from django import forms
from django.utils.translation import ugettext as _

from dbpreferences.forms import DBPreferencesBaseForm

class SearchPreferencesForm(DBPreferencesBaseForm):
    min_term_len = forms.IntegerField(
        help_text=_("Min length of a search term"),
        initial=3, min_value=1
    )
    max_term_len = forms.IntegerField(
        help_text=_("Max length of a search term"),
        initial=50, min_value=1, max_value=200
    )
    max_results = forms.IntegerField(
        help_text=_("Number of the paged for the result page"),
        initial=20, min_value=1, max_value=200
    )
    text_cutout_len = forms.IntegerField(
        help_text=_("The length of the text-hit-cutouts"),
        initial=50, min_value=1, max_value=200
    )
    text_cutout_lines = forms.IntegerField(
        help_text=_("Max. cutout lines for every search term"),
        initial=5, min_value=1, max_value=20
    )

    ban_limit = forms.IntegerField(
        help_text=_("Numbers of limit overstepping after IP would be banned."),
        initial=5, min_value=1, max_value=20
    )
    min_pause = forms.IntegerField(
        help_text=_("Minimum pause in seconds between two search from the same user. (Used 'REMOTE_ADDR')"),
        initial=3, min_value=1, max_value=60
    )
#    max_

    class Meta:
        app_label = 'search'
