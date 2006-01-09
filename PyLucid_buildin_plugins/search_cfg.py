#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "The builtin search"
__long_description__ = """
A small search engine with rating for your CMS.
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
        "get_CGI_data"  : {"search_string": str},
        "internal_page_info" : {
            "name"              : "input_form",
            "description"       : "The HTML form of the search module.",
            "template_engine"   : "string formatting",
            "markup"            : None
        },
    },
    "do_search"       : {
        "must_login"    : False,
        "must_admin"    : False,
        "get_CGI_data"  : {"search_string": str},
    },
}
