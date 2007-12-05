#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information
__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "edit a CMS page"
__long_description__    = """
-Edit/delete existing pages.
-Create new pages.
-Setup the page order in the menu.
"""
__can_deinstall__ = False

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : True,
    "must_admin"    : False,
}
plugin_manager_data = {
    "edit_page" : {
        "must_login"    : True,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "HTML form to edit a CMS Page",
            "markup"            : None,
        },
    },
    "new_page"          : global_rights,
    "delete_page"       : global_rights,
    "tinyTextile_help" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "the tinyTextile help page",
            "markup"            : "textile",
        },
    },
    "select_edit_page" : {
        "must_login"    : True,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "select a page to edit it",
            "markup"            : None,
        },
    },
    "delete_pages" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "select pages to delete these.",
            "markup"            : None,
        },
    },
    "sequencing" : {
        "must_login"    : True,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "change the position of every page",
            "markup"            : None,
        },
    },
    "tag_list": {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "List of all available lucid tags/functions",
            "markup"            : None,
        },
    }
}
