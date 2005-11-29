#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Edit the look of your CMS"
__long_description__ = """
Edit stylesheets, templates and internal_pages
"""
__essential_buildin__ = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "stylesheet" : {
        "must_login"    : True,
        "must_admin"    : True,
        "CGI_dependent_actions": {
            "edit_style": {
                "CGI_laws"      : {"edit": "edit"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"id": int},
                "internal_page_info" : {
                    "description"   : "edit a CSS stylesheet",
                    "markup"        : "string formatting",
                },
            },
            "del_style": {
                "CGI_laws"      : {"del": "del"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"id": int}
            },
            "clone_style": {
                "CGI_laws"      : {"clone": "clone"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"clone_name": str, "new_name": str},
            },
            "save_style": {
                "CGI_laws"      : {"save": "save"},
                "get_CGI_data"  : {"id": int, "name": str, "description": str, "content": str},
            },
        },
        "internal_page_info" : {
            "name"          : "select_style",
            "description"   : "select a stylesheet to edit it",
            "markup"        : "string formatting",
        },
    },

    "template": {
        "must_login"    : True,
        "must_admin"    : True,
        "CGI_dependent_actions" : {
            "edit_template": {
                "CGI_laws"      : {"edit": "edit"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"id": int},
                "internal_page_info" : {
                    "description"   : "edit a page template",
                    "markup"        : "string formatting",
                },
            },
            "del_template": {
                "CGI_laws"      : {"del": "del"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"id": int}
            },
            "clone_template": {
                "CGI_laws"      : {"clone": "clone"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"clone_name": str, "new_name": str},
            },
            "save_template": {
                "CGI_laws"      : {"save": "save"},
                "get_CGI_data"  : {"id": int, "name": str, "description": str, "content": str},
            },
        },
        "internal_page_info" : {
            "name"          : "select_template",
            "description"   : "select a template to edit it",
            "markup"        : "string formatting",
        },
    },

    "internal_page" : {
        "must_login"    : True,
        "must_admin"    : True,
        "CGI_dependent_actions" : {
            "edit_internal_page": {
                "CGI_laws"      : {"edit": "edit"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"internal_page_name": str},
                "internal_page_info" : {
                    "description"   : "edit a internal page",
                    "markup"        : "string formatting",
                },
            },
            "save_internal_page"        : {
                "CGI_laws"      : {"save": "save"}, # Wert vom angeklicken Button
                "get_CGI_data"  : {"internal_page_name": str, "content": str, "description": str, "markup": int},
            },
        },
        "internal_page_info" : {
            "name"          : "select_internal_page",
            "description"   : "select a internal page to edit it",
            "markup"        : "string formatting",
        },
    },
}
