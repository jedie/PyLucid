#!/usr/bin/python
# -*- coding: UTF-8 -*-

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
    "menu" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "name"              : "administation_menu",
            "description"       : "Plugin admin menu",
            "markup"            : None,
        },
    },
    "plugin_setup" : {
        "must_login"    : True,
        "must_admin"    : True,
#        "internal_page_info" : {
#            "name"              : "administation_menu",
#            "description"       : "Plugin admin menu",
#            "markup"            : None,
#        },
    },
}
