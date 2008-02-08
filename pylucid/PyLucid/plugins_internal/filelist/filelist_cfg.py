#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Ibon, Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Media file list"
__long_description__ = """
List files in yor media dir (MEDIA_ROOT), create and delete files and
directories

Settings.py

MEDIA_ROOT = "/home/userjk/pylucid/PyLucid_v0.8RC2_full/pylucid/media"

Need Page Internals: file_form.html
"""

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "file_form",
            "description"       : "The HTML for the file list.",
            "markup"            : None
        },
    },

}
