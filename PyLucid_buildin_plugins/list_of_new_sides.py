#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:list_of_new_sides />
Generiert eine Liste der "letzten Änderungen"
"""

__version__="0.0.6"

__history__="""
v0.0.6
    - Anpassung an neuen Modul-Manager
v0.0.5
    - Anpassung an neuer Absolute-Seiten-Addressierung
v0.0.4
    - Bugfix: SQL Modul wird anders eingebunden
v0.0.3
    - Anpassung an index.py (Rendern der CMS-Seiten mit Python'CGIs)
    - SQL-Connection wird nun auch beendet
v0.0.2
    - Anpassung an neue SQL.py Version
    - Nur Seiten Anzeigen, die auch permitViewPublic=1 sind (also öffentlich)
v0.0.1
    - erste Version
"""


import cgitb;cgitb.enable()


# Python-Basis Module einbinden
import cgi, re

if __name__ == "__main__":
    # Für einen Lokalen Test
    import sys
    sys.path.insert( 0, "../" )



class list_of_new_sides:

    #_______________________________________________________________________
    # Module-Manager Daten

    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "lucidTag" : {
            "must_login"    : False,
            "must_admin"    : False,
        }
    }

    #_______________________________________________________________________

    def __init__( self, PyLucid ):
        #~ self.CGIdata        = PyLucid["CGIdata"]
        self.db             = PyLucid["db"]
        self.config         = PyLucid["config"]
        self.tools          = PyLucid["tools"]

    def lucidTag( self ):
        """
        Aufruf über <lucidTag:list_of_new_sides />
        """
        SQLresult = self.db.select(
            select_items    = [ "id", "name", "title", "lastupdatetime" ],
            from_table      = "pages",
            where           = ( "permitViewPublic", 1 ),
            order           = ( "lastupdatetime", "DESC" ),
            limit           = ( 0, 5 )
        )

        print '<ul id="ListOfNewSides">'

        self.url_entry  = '<li>%(date)s - <a href="'
        self.url_entry += self.link_url
        self.url_entry += '%(link)s">%(title)s</a></li>\n'

        for item in SQLresult:
            prelink = self.db.get_page_link_by_id( item["id"] )
            linkTitle   = item["title"]

            if (linkTitle == None) or (linkTitle == ""):
                # Eine Seite muß nicht zwingent ein Title haben
                linkTitle = item["name"]

            print self.url_entry % {
                "date"  : self.tools.convert_date_from_sql( item["lastupdatetime"] ),
                "link"  : prelink,# + item["name"],
                "title" : cgi.escape( linkTitle ),
            }

        print "</ul>"













