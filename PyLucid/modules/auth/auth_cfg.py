#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "JS-MD5-Login/-Logout"
__long_description__ = """The JS-MD5-Login handler"""
__essential_buildin__ = True

#_____________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "login" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "input_password",
            "description"       : "Login Step-2: Password input form",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "login fake": { # Fake Methode, nur für die zusätzliche interne Seite!
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "name"              : "input_username",
            "description"       : "Login Step-1: Username input form",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "logout" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "pass_reset_form" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "The password reset html form page",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "check_pass_reset" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "pass_reset_email",
            "description"       : "The email with the password reset link",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "pass_reset" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
}
