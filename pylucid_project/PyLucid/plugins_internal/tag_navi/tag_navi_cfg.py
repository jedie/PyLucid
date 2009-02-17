# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information
__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "A tag based navigation"
__long_description__ = """
A simple tag based navigation
"""

#_____________________________________________________________________________
# preferences

#from django import forms
#from django.utils.translation import ugettext as _

#class PreferencesForm(forms.Form):
#    """
#    Links:
#    * http://www.flv-player.net/
#    """
#    internal_page_name = forms.CharField(
#        initial = "flv_player_maxi1",
#        help_text = _(
#            "Default video player template"
#            " (internal page name without file externsion)."
#        ),
#    )
#    swf_file = forms.CharField(
#        initial = "flv_player_maxi",
#        help_text = _("swf player filename (without file externsion)."),
#    )
#    config = forms.CharField(
#        initial = (
#            "loop=1\n"
#            "showvolume=1\n"
#            "showtime=1\n"
#        ),
#        help_text = _("swf player configuration text (FlashVars)."),
#        widget=forms.Textarea(attrs={'rows': '15'}),
#    )

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : False,
    "must_admin"    : False,
}

plugin_manager_data = {
    "lucidTag" : global_rights,
    "page_list": global_rights,
}
