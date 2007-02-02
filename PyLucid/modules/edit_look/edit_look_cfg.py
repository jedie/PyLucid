#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Edit the look of your CMS"
__long_description__ = """
Edit stylesheets, templates and internal_pages
"""
__essential_buildin__ = True

#_____________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

global_rights = {
    "must_login"    : True,
    "must_admin"    : True,
}

module_manager_data = {
    "stylesheet" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "name"              : "select_style",
            "description"       : "select a stylesheet to edit it",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "edit_style": {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "edit a CSS stylesheet",
            "template_engine"   : "string formatting",
            "markup"            : None
        },
    },
    "del_style": global_rights,
    "clone_style": global_rights,
    "save_style": global_rights,
    #-------------------------------------------------------------------------
    "template": {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "name"              : "select_template",
            "description"       : "select a template to edit it",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "edit_template": {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "edit a page template",
            "template_engine"   : "string formatting",
            "markup"            : None
        },
    },
    "del_template": global_rights,
    "clone_template": global_rights,
    "save_template": global_rights,
    #-------------------------------------------------------------------------
    "internal_page" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "name"              : "select_internal_page",
            "description"       : "select a internal page to edit it",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },

    "edit_internal_page": {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "edit a internal page",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "save_internal_page": global_rights,
    "download_internal_page": global_rights,
    "save_all_local": global_rights,
    "internal_page_diff": global_rights,
}
