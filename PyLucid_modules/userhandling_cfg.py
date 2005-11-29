#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "User Handling"
__long_description__    = """User data administration"""
__essential_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "manage_user": {
        "must_login"    : True,
        "must_admin"    : True,
        "CGI_dependent_actions": {
            "save_changes": {
                "CGI_laws"      : {"save": "save"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"id": int, "name": str, "email": str, "realname": str, "admin": int}
            },
            "add_user": {
                "CGI_laws"      : {"add user": "add user"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"username": str, "email": str, "realname": str, "admin": int}
            },
            "del_user": {
                "CGI_laws"      : {"del": "del"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"id": int}
            },
        }
    },
    "add_user" : {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "pass_recovery" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "send_email" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
}
