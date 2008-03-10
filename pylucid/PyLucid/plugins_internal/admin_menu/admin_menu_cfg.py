#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information
__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Administration Menu"
__long_description__ = """"""
__can_deinstall__ = False

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : True,
    "must_admin"    : True,
}
plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : True,
        "must_admin"    : False,
        "has_Tags"      : True,
        "no_rights_error" : True, # TODO: remove in v0.9, see: ticket:161
    },
    "edit_page_link"    : global_rights,
    "new_page_link"     : global_rights,
    "del_page_link"     : global_rights,
    "sub_menu_link"     : global_rights,
    "sub_menu"          : {
        "must_login"    : True,
        "must_admin"    : False,
    },
}
