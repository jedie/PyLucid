#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Include local sourcecode file into your page."
__long_description__ = """
Includes a local sourcecode file into your cms page and hightlight it.
"""
__important_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "lucidFunction" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "download" : {
        "must_login"    : False,
        "must_admin"    : False,
        "get_CGI_data"  : {"file": str},
        "direct_out"    : True,
    },
}
