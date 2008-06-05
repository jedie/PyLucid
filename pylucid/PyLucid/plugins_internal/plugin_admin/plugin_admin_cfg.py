# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "The Plugin Administration"
__long_description__    = """With the plugin Administration
you can install/deinstall plugins and activate/deactivate them in the DB.
"""
__cannot_deinstall__ = True

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "menu": {
        "must_login": True,
        "must_admin": True,
        "admin_sub_menu": {
            "section"       : _("setup"),
            "title"         : _("Plugin administration"),
            "help_text"     : _(
                "Manage all PyLucid plugins."
            ),
            "open_in_window": False,
            "weight" : -8,
        },
    },
    "plugin_setup": {
        "must_login": True,
        "must_admin": True,
    },
}
