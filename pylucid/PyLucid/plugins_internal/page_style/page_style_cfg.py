# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "Stylesheet module"
__long_description__ = """Puts the Stylesheet into the CMS page."""
__can_deinstall__ = False

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : False,
    "must_admin"    : False,
}
plugin_manager_data = {
    "lucidTag" : global_rights,
    "print_current_style" : global_rights,
    "sendStyle" : global_rights,
}
