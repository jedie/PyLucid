# coding: utf-8


from django import forms
from django.utils.translation import ugettext as _

from dbpreferences.forms import DBPreferencesBaseForm

class FindReplacePreferencesForm(DBPreferencesBaseForm):
    min_term_len = forms.IntegerField(
        help_text=_("Min length of a search term"),
        initial=3, min_value=1
    )
    max_term_len = forms.IntegerField(
        help_text=_("Max length of a search term"),
        initial=254, min_value=1, max_value=2000
    )
    text_cutout_len = forms.IntegerField(
        help_text=_("The length of the text-hit-cutouts"),
        initial=50, min_value=1, max_value=200
    )
    text_cutout_lines = forms.IntegerField(
        help_text=_("Max. cutout lines for every search term"),
        initial=5, min_value=1, max_value=20
    )

    class Meta:
        app_label = 'find_and_replace'


def get_preferences():
    pref_form = FindReplacePreferencesForm()
    preferences = pref_form.get_preferences()
    return preferences
