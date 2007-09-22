#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "Stylesheet module"
__long_description__ = """Puts the Stylesheet into the CMS page."""
__can_deinstall__ = False

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            # Note: This internal page is not used in page_style.lucidTag()
            # The data used in PyLucid.middlewares.additional_content!
            "name"              : "add_data",
            "description"       : "Template for adding CSS/JS from plugins.",
            "markup"            : None
        },
    },
    "print_current_style" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "write_styles",
            "description"       : "Insert the stylesheets directly.",
            "markup"            : None
        },
    },
    "sendStyle" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
}
