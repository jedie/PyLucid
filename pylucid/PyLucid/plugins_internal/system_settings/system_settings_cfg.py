#!/usr/bin/python
# -*- coding: UTF-8 -*-

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

from django import newforms as forms
from django.utils.translation import ugettext as _

from PyLucid.db.page import PageChoiceField, get_page_choices


class PreferencesForm(forms.Form):
    index_page = PageChoiceField(
        widget=forms.Select(choices=get_page_choices()),
        help_text=_("The page ID of the index page"),
        initial=0
    )
    auto_shortcuts = forms.BooleanField(
        help_text=_("Should the shortcut of a page rebuild on every edit?"),
        initial=True
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
