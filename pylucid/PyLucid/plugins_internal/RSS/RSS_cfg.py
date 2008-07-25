# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "A RSS feed reader"
__long_description__ = """
This lucidFunction read from a given URL the RSS feed ans integrade
it on your CMS Page.
"""

#_____________________________________________________________________________
# preferences

from django.conf import settings

from django import forms
from django.utils.translation import ugettext as _

class PreferencesForm(forms.Form):
#    url = forms.URLField(
#        initial="http://sourceforge.net/export/rss2_projnews.php?group_id=146328",
#        min_length = 15,
#        verify_exists = True,
#        label=_("feed URL"),
#        help_text = _("The URL address of the RSS feed."),
#        widget=forms.TextInput(attrs={'class':'bigger'}),
#    )
    # FIXME: Create a choice field thats listed all existing files.
    internal_page = forms.CharField(
        initial="RSS",
        help_text = _(
            "The template filename for this feed."
            " (The internal page stored in %s or %s)"
        ) % (settings.INTERNAL_PAGE_DIR, settings.CUSTOM_INTERNAL_PAGE_DIR),
    )
    timeout = forms.IntegerField(
        initial = 1,
        min_value = 1,
        max_value = 60,
        help_text=_("socket timeout for getting the RSS feed.")
    )
    debug = forms.BooleanField(
        initial=False, required=False,
        help_text=_(
            "Display the raw parsed feed?"
            " Usefull to edit the template for this feed."
        ),
    )

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "debug" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
}
