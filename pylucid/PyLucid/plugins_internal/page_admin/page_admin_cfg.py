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
    "edit_page" : global_rights,
    "new_page" : global_rights,
    "delete_page" : global_rights,
    "tinyTextile_help" : {
        "must_login" : False,
        "must_admin" : False,
    },
    "select_edit_page" : global_rights,
    "delete_pages" : {
        "must_login" : True,
        "must_admin" : True,
    },
    "sequencing" : global_rights,
    "tag_list": {
        "must_login" : False,
        "must_admin" : False,
    }
}
