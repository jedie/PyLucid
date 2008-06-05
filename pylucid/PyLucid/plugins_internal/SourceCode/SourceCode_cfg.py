# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Include local sourcecode file into your page."
__long_description__ = """
Includes a local sourcecode file into your cms page and hightlight it.
"""

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "download" : {
        "must_login"    : False,
        "must_admin"    : False,
        "direct_out"    : True,
    },
}
