# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "The presentation plugin"
__long_description__    = __description__

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login": False,
    "must_admin": False,
}
plugin_manager_data = {
    "menu" : global_rights,
    "all_pages": global_rights,
}
