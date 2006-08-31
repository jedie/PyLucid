#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Shows internal information"
__long_description__ = """
Shows internal, system and python information.
"""
__important_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {

    "link": {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "menu": {
        "must_login"    : True,
        "must_admin"    : True,
    },

    "system_info": {
        "must_login"        : True,
        "must_admin"        : True,
        "menu_section"      : "system",
        "menu_description"  : "System Info",
    },
    "session_data": {
        "must_login"        : True,
        "must_admin"        : True,
        "menu_section"      : "system",
        "menu_description"  : "Session data",
    },
    "log_data": {
        "must_login"        : True,
        "must_admin"        : True,
        "menu_section"      : "system",
        "menu_description"  : "LOG data",
    },
    "sql_status": {
        "must_login"        : True,
        "must_admin"        : True,
        "menu_section"      : "SQL",
        "menu_description"  : "SQL table status",
    },
    "optimize_sql_tables": {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "python_modules": {
        "must_login"        : True,
        "must_admin"        : True,
        "menu_section"      : "misc",
        "menu_description"  : "Display all Python Modules",
    },
    "module_info": {
        "must_login"    : True,
        "must_admin"    : True,
    },
}
