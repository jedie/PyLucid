#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
"""

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "edit a CMS page"
__long_description__    = """Edit a normal CMS pages"""
__essential_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

module_manager_data = {
    "edit_page" : {
        "must_login"    : True,
        "must_admin"    : False,
        "CGI_dependent_actions" : {
            "preview"   : {
                "CGI_laws"      : {"preview": "preview"}, # Submit-input-Button
                "get_CGI_data"  : {"page_id": int},
            },
            "save"      : {
                "CGI_laws"      : {"save": "save"}, # Submit-input-Button
                "get_CGI_data"  : {"page_id": int},
            },
        },
        "internal_page_info" : {
            "description"       : "HTML form to edit a CMS Page",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },
    "select_edit_page" : {
        "must_login"    : True,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "select a page to edit it",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },
    "new_page" : {
        "must_login"    : True,
        "must_admin"    : True,
        "CGI_dependent_actions" : {
            "preview": {
                "CGI_laws"      : {"preview": "preview"}, # Submit-input-Button
                "get_CGI_data"  : {"page_id": int},
            },
            "save_new": {
                "CGI_laws"      : {"save": "save"}, # Submit-input-Button
            },
        }
    },
    "select_del_page" : {
        "must_login"    : True,
        "must_admin"    : True,
        "CGI_dependent_actions" : {
            "delete_page"       : {
                "CGI_laws"      : {"delete page":"delete page"}, # Submit-input-Button
                "get_CGI_data"  : {"side_id_to_del": int},
            },
        },
        "internal_page_info" : {
            "description"       : "select a page to delete it",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },
    "sequencing" : {
        "must_login"    : True,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "change the position of every page",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },
    "save_positions" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
}
