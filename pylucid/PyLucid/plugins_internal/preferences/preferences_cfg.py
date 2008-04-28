#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "low level preference editor"
__long_description__ = """
A low level editor for the preferences.
"""

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : True,
    "must_admin"    : True,
}

plugin_manager_data = {
    "select" : global_rights,
    "edit": global_rights,
}
