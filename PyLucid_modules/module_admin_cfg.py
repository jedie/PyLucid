#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "The Module/Plugin Administration"
__essential_buildin__   = True

# Ausnahme: install_template wird in install_PyLucid.py benötigt!
import os
f = file(os.path.join("PyLucid_modules","module_admin_administation_menu.html"),"rU")
install_template = f.read()
f.close()

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "menu" : {
        "must_login"    : True,
        "must_admin"    : True,
    },

    "administation_menu" : {
        "must_login"        : True,
        "must_admin"        : True,
        "menu_section"      : "Admin",
        "menu_description"  : "Administation menu",
        "internal_page_info" : {
            "description"   : "The Module/Plugin Administration page",
            "markup"        : "TAL",
        },
    },
    "debug_installed_modules_info" : {
        "must_login"        : True,
        "must_admin"        : True,
        "menu_section"      : "misc",
        "menu_description"  : "debug install Modules/Plugins config data",
    },

    "first_time_install" : {
        "must_login"        : True,
        "must_admin"        : True,
        "menu_section"      : "misc",
        "menu_description"  : "first time install (deletes existing tables!)",
        "CGI_dependent_actions": {
            "first_time_install_confirmed": {
                "CGI_laws"      : {"confirm": "yes"},
            },
        },
    },

    "install" : {
        "must_login"    : True,
        "must_admin"    : True,
        "get_CGI_data"  : {"package": str, "module_name": str},
    },

    "deinstall" : {
        "must_login"    : True,
        "must_admin"    : True,
        "get_CGI_data"  : {"id": int},
    },

    "reinit" : {
        "must_login"    : True,
        "must_admin"    : True,
        "get_CGI_data"  : {"id": int},
    },

    "activate" : {
        "must_login"    : True,
        "must_admin"    : True,
        "get_CGI_data"  : {"id": int},
    },

    "deactivate" : {
        "must_login"    : True,
        "must_admin"    : True,
        "get_CGI_data"  : {"id": int},
    },
}
