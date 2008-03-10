#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "The builtin search"
__long_description__ = """
A small search engine with rating for your CMS.
"""

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login": False,
    "must_admin": False,
}
plugin_manager_data = {
    "lucidTag": global_rights,
    "do_search": global_rights,
}
