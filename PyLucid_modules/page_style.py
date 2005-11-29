#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""

"""

__version__="0.1.0"

__history__="""
v0.1.0
    -  erste Version
"""

import sys

class page_style:

    #_______________________________________________________________________
    # Module-Manager Daten

    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "lucidTag" : {
            "must_login"    : False,
            "must_admin"    : False,
        },
        "print_current_style" : {
            "must_login"    : False,
            "must_admin"    : False,
        },
        "embed" : {
            "must_login"    : False,
            "must_admin"    : False,
            "get_CGI_data"  : {"page_id": int},
            #~ "direct_out"    : True,
        },
    }

    #_______________________________________________________________________

    def __init__(self, PyLucid):
        self.db = PyLucid["db"]
        self.URLs = PyLucid["URLs"]

    def lucidTag(self):
        sys.stdout.write(
            '<link rel="stylesheet" type="text/css" href="%s%s" />' % (self.URLs["action"], "print_current_style")
        )

    def print_current_style(self):
        """
        Dies ist nur eine pseudo-Methode, denn die CSS anfrage wird direkt in der
        index.py mit check_CSS_request() beantwortet!
        """
        self.page_msg("print_current_style() ERROR!!!")

    def embed(self, page_id):
        print '<style type="text/css">'
        print self.db.side_style_by_id(page_id)
        print '</style>'
