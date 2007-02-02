#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "page update list"
__long_description__ = """
Generate a list of the last page updates.
"""
__important_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "PageUpdateTable",
            "description"       : "Table for the list of page updates",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "lucidFunction": {
        "must_login"    : False,
        "must_admin"    : False,
    }
}
