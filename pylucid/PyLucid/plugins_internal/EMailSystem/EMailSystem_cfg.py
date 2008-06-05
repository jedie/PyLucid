# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "send EMails to other PyLucid user."
__long_description__    = """With this Plugin you can send EMails to other
PyLucid users."""
__can_deinstall__ = True

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "user_list" : {
        "must_login"    : True,
        "must_admin"    : False,
        "admin_sub_menu": {
            "section"       : _("user management"),
            "title"         : _("EMail system"),
            "help_text"     : _("Send other PyLucid members a email."),
            "open_in_window": False,
            "weight" : 0,
        },
    },
}
