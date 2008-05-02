#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Find & replace content in all pages/templates/shylesheets."
__long_description__ = """
A simple find & replace plugin for all pages/templates/shylesheets content.
You can easy change e.g. a URL in every page content or correct a misspelled
word everywhere. Also useable to change CSS colors everywhere.

Note: This plugin can only administrator used! You find the plugin in the
submenu.
"""

#_____________________________________________________________________________
# preferences

from django import newforms as forms
from django.utils.translation import ugettext as _

class PreferencesForm(forms.Form):
    min_term_len = forms.IntegerField(
        help_text=_("Min length of a search term"),
        initial=2, min_value=1
    )
    max_term_len = forms.IntegerField(
        help_text=_("Max length of a search term"),
        initial=150, min_value=1, max_value=500
    )

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "find_and_replace" : {
        "must_login"    : True,
        "must_admin"    : True,
    },
}

preferences = (
    {
        "name": "term len limit",
        "description": "How min/max long must a search term be?",
        "value": {
            "min term len": 1,
            "max term len": 255,
        }
    },
)