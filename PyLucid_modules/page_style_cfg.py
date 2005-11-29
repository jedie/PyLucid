#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "Stylesheet module"
__essential_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

module_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "print_current_style" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "embed" : {
        "must_login"    : False,
        "must_admin"    : False,
        "get_CGI_data"  : {"page_id": int},
        #~ "direct_out"    : True,
    },
}
