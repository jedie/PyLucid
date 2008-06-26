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

from django import newforms as forms
from django.utils.translation import ugettext as _

from PyLucid.db.page import PageChoiceField, get_page_choices


class PreferencesForm(forms.Form):
    index_page = PageChoiceField(
        widget=forms.Select(choices=get_page_choices()),
        help_text=_("The page ID of the index page"),
        initial=None
    )
    auto_shortcuts = forms.BooleanField(
        help_text=_("Should the shortcut of a page rebuild on every edit?"),
        initial=True
    )

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {}
