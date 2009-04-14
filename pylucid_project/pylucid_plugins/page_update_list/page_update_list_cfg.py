# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "page update list"
__long_description__ = """
Generate a list of the last page updates.
"""

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : False,
    "must_admin"    : False,
}
plugin_manager_data = {
    "lucidTag" : global_rights,
    "lucidFunction": global_rights,
}
