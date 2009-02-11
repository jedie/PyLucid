# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "Stylesheet module"
__long_description__ = """Puts the Stylesheet into the CMS page."""
__can_deinstall__ = False

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : False,
    "must_admin"    : False,
}
plugin_manager_data = {
    "lucidTag" : global_rights,
    "print_current_style" : global_rights,
    "sendStyle" : global_rights,
    "switch" : {
        "must_login"    : True,
        "must_admin"    : False,
        "admin_sub_menu": {
            "section"       : _("edit look"),
            "title"         : _("Template/Style switcher"),
            "help_text"     : _(
                "Overwrite the associated template/stylesheet"
                " (Good for testing new templates/styles)."
            ),
            "open_in_window": False,
            "weight" : -5,
        },
    },
}
