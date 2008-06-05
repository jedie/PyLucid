# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information
__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "JS-SHA-Login/-Logout"
__long_description__ = """The JS-SHA-Login handler"""

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login": False,
    "must_admin": False,
}
plugin_manager_data = {
    "login": global_rights,
    "logout": global_rights,
    "pass_reset": global_rights,
    "new_password": global_rights,
}
