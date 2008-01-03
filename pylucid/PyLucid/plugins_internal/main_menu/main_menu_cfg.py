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
                "name"              : "menu",
                "description"       : "Base Menu Structure",
                "markup"            : None
                },
            },
        "_menu_item" : { # Fake for internal page
            "must_login"        : True,
            "must_admin"        : True,
            "internal_page_info": {
                "name"              : "menu_item",
                "description"       : "Menu Item",
                "markup"            : None
                },
            },
        "_menu_item_current" : { # Fake for internal page
            "must_login"        : True,
            "must_admin"        : True,
            "internal_page_info": {
                "name"              : "menu_item_current",
                "description"       : "Selected Menu Item",
                "markup"            : None
                },
            },
        }