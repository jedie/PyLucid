#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Administration Menu"
__long_description__ = """"""
__essential_buildin__ = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

global_rights = {
    "must_login"    : True,
    "must_admin"    : True,
    "has_Tags"      : False,
}

module_manager_data = {
    "lucidTag" : {
        "must_login"    : True,
        "must_admin"    : False,
        "has_Tags"      : True,
        "no_rights_error" : True, # Fehlermeldung, wenn der User nicht eingeloggt ist, wird nicht angezeigt
        "internal_page_info" : {
            "name"              : "top_menu",
            "description"       : "Administration front menu",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },
    "edit_page_link"    : global_rights,
    "new_page_link"     : global_rights,
    "del_page_link"     : global_rights,
    "sub_menu_link"     : global_rights,
    "sub_menu"          : {
        "must_login"    : True,
        "must_admin"    : False,
        "has_Tags"      : True,
        "internal_page_info" : {
            "name"              : "sub_menu",
            "description"       : "Administration sub menu",
            "template_engine"   : "string formatting",
            "markup"            : "textile",
        },
    },
}
