#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "Makes a MySQL dump for a backup"
__long_description__ = """
You can make a SQL dump from you DB. Also you can make a install-dump.
"""
__important_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "menu" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "MySQL dump Menu",
            "template_engine"   : "string formatting",
            "markup"            : None
        },
    },
    "display_help"      : {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "display_dump"      : {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "display_command"   : {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "download_dump" : {
        "must_login"    : True,
        "must_admin"    : True,
        "direct_out"    : True,
        "sys_exit"      : True, # Damit ein sys.exit() auch wirklich fuktioniert
    }
}
