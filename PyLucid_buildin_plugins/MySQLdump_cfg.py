#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "Makes a MySQL dump for a backup"
__important_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

global_rights = {
        "must_login"    : True,
        "must_admin"    : True,
}

module_manager_data = {
    "menu" : global_rights,

    "display_help"      : global_rights,
    "display_dump"      : global_rights,
    "display_command"   : global_rights,
    "download_dump" : {
        "must_login"    : True,
        "must_admin"    : True,
        "direct_out"    : True,
        "sys_exit"      : True, # Damit ein sys.exit() auch wirklich fuktioniert
    }
}
