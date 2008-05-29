#!/usr/bin/python
# -*- coding: UTF-8 -*-

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

from django import newforms as forms
from django.utils.translation import ugettext as _

#class PreferencesForm(forms.Form):
#    video_player = forms.BooleanField(
#        initial = "flv_player.swf",
#        help_text = _(
#            "Video Player file (from http://www.flv-player.net)"
#        ),
#    )
#    print_index = forms.BooleanField(
#        initial = False,
#        help_text = _('If checked every back link bar starts with a link to "index_url"'),
#    )
#    index_url = forms.CharField(
#        initial = "/",
#        help_text = _("The url used for print_index. Note: not verify if the url exists."),
#    )
#    index = forms.CharField(
#        initial = _("Index"),
#        help_text = _('the name that is printed for the indexpage'),
#    )

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "upload": {
        "must_login": True,
        "must_admin": False,
        "admin_sub_menu": {
            "section"       : _("multimedia"), # The sub menu section
            "title"         : _("new flash video"),
            "help_text"     : _("Upload a new flash video file."),
            "open_in_window": False, # Should be create a new JavaScript window?
            "weight" : 0, # sorting wieght for every section entry
        },

    },
}
