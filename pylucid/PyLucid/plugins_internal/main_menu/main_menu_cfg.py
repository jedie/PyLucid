#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "A tree main menu"
__long_description__    = __description__

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"        : False,
        "must_admin"        : False,
        "internal_page_info": {
            "name"              : "main_menu",
            "description"       : "Base Menu Structure with the CSS",
            "markup"            : None
            },
        },
    "_main_menu_li" : { # Fake for internal page
        "must_login"        : True,
        "must_admin"        : True,
        "internal_page_info": {
            "name"              : "main_menu_li",
            "description"       : "One list entry in the main menu.",
            "markup"            : None
            },
        },
    "_main_menu_ul" : { # Fake for internal page
        "must_login"        : True,
        "must_admin"        : True,
        "internal_page_info": {
            "name"              : "main_menu_ul",
            "description"       : "One sub list part from the main menu.",
            "markup"            : None
            },
        }
}