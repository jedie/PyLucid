# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information
__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "simple Flash Video Player Plugin (ALPHA state!)"
__long_description__ = """
Used http://www.flv-player.net
"""

#_____________________________________________________________________________
# preferences

from django import forms
from django.utils.translation import ugettext as _

class PreferencesForm(forms.Form):
    """
    Links:
    * http://www.flv-player.net/
    """
    internal_page_name = forms.CharField(
        initial = "flv_player_maxi1",
        help_text = _(
            "Default video player template"
            " (internal page name without file externsion)."
        ),
    )
    swf_file = forms.CharField(
        initial = "flv_player_maxi",
        help_text = _("swf player filename (without file externsion)."),
    )
    config = forms.CharField(
        initial = (
            "loop=1\n"
            "showvolume=1\n"
            "showtime=1\n"
        ),
        help_text = _("swf player configuration text (FlashVars)."),
        widget=forms.Textarea(attrs={'rows': '15'}),
    )

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "admin_menu": {
        "must_login"    : True,
        "must_admin"    : True,
        "admin_sub_menu": {
            "section"       : _("multimedia"), # The sub menu section
            "title"         : _("Flash administation menu"),
            "help_text"     : _("Flash file administration"),
            "open_in_window": False, # Should be create a new JavaScript window?
            "weight" : 0, # sorting wieght for every section entry
        },
    },
    "upload": {
        "must_login": True,
        "must_admin": False,
        "menu_section"      : "admin",
        "menu_description"  : "Upload a new flash video file.",
    },
    "read_filesystem" : {
        "must_login"    : True,
        "must_admin"    : True,
        "menu_section"      : "admin",
        "menu_description"  : "Scan all media path for flash files and add them",
    },
    "list_all" : {
        "must_login"    : True,
        "must_admin"    : False,
        "menu_section"      : "admin",
        "menu_description"  : "List all existing flash videos",
    },
    "preview" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "detail" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
}
