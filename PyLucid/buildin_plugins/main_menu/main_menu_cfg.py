#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "A tree main menu"
__long_description__    = __description__
__important_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "main_menu",
            "description"       : "The main menu Template",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    }
}
