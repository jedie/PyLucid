#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Create a RSS news feed."
__long_description__ = """
Create a RSS news feed from the last 15 page updates.
"""

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "download" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "RSSfeed",
            "description"       : "The RSS feed generator template",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    }
}
