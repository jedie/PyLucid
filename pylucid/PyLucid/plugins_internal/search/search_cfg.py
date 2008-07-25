# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "The builtin search"
__long_description__ = """
A small search engine with rating for your CMS.
"""

#_____________________________________________________________________________
# preferences

from django import forms
from django.utils.translation import ugettext as _

class PreferencesForm(forms.Form):
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

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login": False,
    "must_admin": False,
}
plugin_manager_data = {
    "lucidTag": global_rights,
    "do_search": global_rights,
}
