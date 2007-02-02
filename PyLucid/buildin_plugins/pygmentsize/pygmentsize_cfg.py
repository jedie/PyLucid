#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = __long_description__ = "A small Layer to pygments"

__essential_buildin__ = True

#___________________________________________________________________________________________________
# Module-Manager Daten

module_manager_data = {
    "setup" : {
        "must_login": True,
        "must_admin": True,
        "internal_page_info" : {
            "description"       : "select the default pygments style",
            "template_engine"   : "jinja",
            "markup"            : None,
        },
    },
    "write_sourcecode": {
        "must_login": False,
        "must_admin": False,
        "internal_page_info" : {
            "name"              : "sourcecode_block",
            "description"       : "HTML Fragment for the Sourcecode",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },
}

plugin_cfg = {
    "default_style": "friendly",
}