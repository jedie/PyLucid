#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Login/Logout"
__long_description__ = """"""
__essential_buildin__ = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "login" : {
        "must_login"    : False,
        "direct_out"    : True,
        "internal_page_info" : {
            "description"       : "The Login html-form Page",
            "template_engine"   : "string formatting",
            "markup"            : None
        },
    },
    "logout" : {
        "must_login"    : False,
        "must_admin"    : False,
        "direct_out"    : True,
    },
    "check_login" : {
        "must_login"    : False,
        "direct_out"    : True,
    },
}
