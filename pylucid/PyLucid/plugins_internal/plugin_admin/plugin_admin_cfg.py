#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "The Plugin Administration"
__long_description__    = """With the plugin Administration
you can install/deinstall plugins and activate/deactivate them in the DB.
"""
__cannot_deinstall__ = True

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login": True,
    "must_admin": True,
}
plugin_manager_data = {
    "menu": global_rights,
    "plugin_setup": global_rights,
}
