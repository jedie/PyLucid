#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "The Module/Plugin Administration"
__long_description__    = """With the Module/Plugin Administration
you can install/deinstall modules to the DB and you
can activate/deactivate this modules in the DB.
"""
__essential_buildin__   = True

#_____________________________________________________________________________
# Module-Manager Daten

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
            "description"       : "The Module/Plugin Administration page",
            "template_engine"   : "jinja",
            "markup"            : None
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
    },

    "install" : {
        "must_login"    : True,
        "must_admin"    : True,
    },

    "deinstall" : {
        "must_login"    : True,
        "must_admin"    : True,
    },

    "reinit" : {
        "must_login"    : True,
        "must_admin"    : True,
    },

    "activate" : {
        "must_login"    : True,
        "must_admin"    : True,
    },

    "deactivate" : {
        "must_login"    : True,
        "must_admin"    : True,
    },

    #_________________________________________________________________________

    "module_setup" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "Select a Module to setup it",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
}
