#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben
__author__      = "Benjamin Weber + Jens Diemer"
__url__         = "http://blinx.tippsl.de"
__description__ = "Displays a random text of a Site in PyLucid."
__long_description__ = """
Displays a random text.
"""
__important_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False


global_rights = {
    "must_login"    : False,
    "must_admin"    : False,
}


module_manager_data = {
    "lucidFunction" 	: global_rights,
    "lucidTag" 		: {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "PluginDownload",
            "description"       : "A list of all external plugins",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "download" 		: global_rights,
}
