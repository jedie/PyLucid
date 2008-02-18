#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Find & replace content in all CMS pages."
__long_description__ = """
A simple find & replace plugin. You can easy change e.g. a URL in every page
content or correct a misspelled word everywhere :)
Note: This plugin can only administrator used! You find the plugin in the
submenu.
"""

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "find_and_replace" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "name"              : "find_and_replace",
            "description"       : "HTML page.",
            "markup"            : None
        },
    },
}
