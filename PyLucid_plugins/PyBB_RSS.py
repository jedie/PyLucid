#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:PyBB/>
"""

__version__="0.0.1"

__history__="""
v0.0.1
    - erste Version
"""

import sys

from PyLucid_simpleTAL import simpleTAL, simpleTALES

from PyLucid_plugins import PyBB

#~ print "Content-type: text/html; charset=utf-8\r\n" # Debugging


template = """
<table>
<tr tal:repeat="data example"
tal:attributes="class string:color${'repeat/data/odd'}">
    <td tal:content="repeat/data/number"></td>
    <td tal:content="data/char"></td>
</tr>
</table>
<style type="text/css">
    .color0 {background-color:#EEEEEE;}
    .color1 {background-color:#DDDDDD;}
</style>
"""




class PyBB_RSS:

    #_______________________________________________________________________
    # Module-Manager Daten
    global_rights = {
        "must_login"    : False,
        "must_admin"    : False,
    }

    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "lucidTag" : global_rights,
        "print_summary" : global_rights,

        "view_forum": {
            "must_login"    : False,
            "must_admin"    : False,
            "get_CGI_data"  : {"forum_id": int},
        }
    }

    #_______________________________________________________________________

    def __init__( self, PyLucid ):
        self.CGIdata        = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.db             = PyLucid["db"]
        self.session        = PyLucid["session"]
        #~ self.session.debug()
        self.config         = PyLucid["config"]
        self.preferences    = PyLucid["preferences"]

        self.PyBB = PyBB.PyBB_routines.PyBB(PyLucid, "PyBB_RSS")

        self.bb_table_prefix = "phpbb_"

    def lucidTag(self):
        categories = self.PyBB.categories()
        forums = self.PyBB.forums()
        forums = self.db.decode_sql_results(forums, codec="latin-1")
        print forums

    def print_summary(self):
        self.PyBB.print_summary()

    def view_forum(self, forum_id):
        self.PyBB.view_forum(forum_id)




