#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "page update list"
__long_description__ = """
Generate a list of the last page updates.
"""

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "PageUpdateTable",
            "description"       : "Table for the list of page updates",
            "markup"            : None
        },
    },
    "lucidFunction": {
        "must_login"    : False,
        "must_admin"    : False,
    }
}
