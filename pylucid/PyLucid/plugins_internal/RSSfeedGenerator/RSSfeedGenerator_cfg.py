# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Create a RSS news feed."
__long_description__ = """
Create a RSS news feed from the last 15 page updates.
"""

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : False,
    "must_admin"    : False,
}
plugin_manager_data = {
    "lucidTag" : global_rights,
    "download" : global_rights,
}
