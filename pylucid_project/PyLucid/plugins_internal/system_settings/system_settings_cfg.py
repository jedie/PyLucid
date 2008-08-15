# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "System settings"
__long_description__ = """
A pseudo plugin for holding the system settings via the plugin preferences.
"""

#_____________________________________________________________________________
# preferences

from django import forms
from django.utils.translation import ugettext as _

from PyLucid.db.page import PageChoiceField, get_page_choices


class PreferencesForm(forms.Form):
    index_page = PageChoiceField(
        initial=None,
        widget=forms.Select(choices=get_page_choices()),
        help_text=_("The page ID of the index page"),
    )
    auto_shortcuts = forms.BooleanField(
        initial=True, required=False,
        help_text=_("Should the shortcut of a page rebuild on every edit?"),
    )

# Optional, this Plugin can't have multiple preferences
multiple_pref = False

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {}
