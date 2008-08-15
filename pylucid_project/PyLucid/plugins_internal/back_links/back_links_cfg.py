# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information
__author__              = "Jens Diemer, Manuel Herzog"
__url__                 = "http://www.PyLucid.org"
__description__         = "A small Backlink generator"
__long_description__ = """
Puts links to every lower level page into the CMS page.
"""

#_____________________________________________________________________________
# preferences

from django import forms
from django.utils.translation import ugettext as _

class PreferencesForm(forms.Form):
    print_last_page = forms.BooleanField(
        initial = True, required=False,
        help_text = _(
            "If checked the actual page will be the last page in the bar."
            " Otherwise the parentpage."
        ),
    )
    print_index = forms.BooleanField(
        initial = False, required=False,
        help_text = _('If checked every back link bar starts with a link to "index_url"'),
    )
    index_url = forms.CharField(
        initial = "/",
        help_text = _("The url used for print_index. Note: not verify if the url exists."),
    )
    index = forms.CharField(
        initial = _("Index"),
        help_text = _('the name that is printed for the indexpage'),
    )

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    }
}
