# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Preference editor"
__long_description__ = """
A editor for the preferences.
"""

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "select" : {
        "must_login"    : True,
        "must_admin"    : True,
        "admin_sub_menu": {
            "section"       : _("setup"),
            "title"         : _("Preferences editor"),
            "help_text"     : _(
                "Setup all plugin preferences."
            ),
            "open_in_window": False,
            "weight" : -5,
        },
    },
    "edit": {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "add": {
        "must_login"    : True,
        "must_admin"    : True,
    },

}