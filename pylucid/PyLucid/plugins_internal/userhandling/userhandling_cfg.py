#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "User Handling"
__long_description__    = """User data administration"""

#_____________________________________________________________________________
# plugin administration data

module_manager_data = {
    "manage_user": {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "user_table": {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "Edit user table",
            "template_engine"   : "jinja",
            "markup"            : None,
        },
    },
    "add_user" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "HTML Form to add a new User",
            "template_engine"   : "jinja",
            "markup"            : None,
        },
    },
    "new_password_form" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "Form to send the new password",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "set_new_password" : {
        "must_login"    : True,
        "must_admin"    : True,
    },
}
