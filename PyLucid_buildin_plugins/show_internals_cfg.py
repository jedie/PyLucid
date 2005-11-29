#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Einstellungsdaten zu "show internals"
"""

__author__ = "Jens Diemer"


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
