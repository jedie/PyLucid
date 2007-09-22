#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Create a RSS news feed."
__long_description__ = """
Create a RSS news feed from the last 15 page updates.
"""

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
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
            "markup"            : None
        },
    }
}
