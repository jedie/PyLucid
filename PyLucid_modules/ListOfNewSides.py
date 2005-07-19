#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert eine Liste der "letzten Änderungen"
"""

__version__="0.0.5"

__history__="""
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
import re

if __name__ == "__main__":
    # Für einen Lokalen Test
    import sys
    sys.path.insert( 0, "../" )


#_______________________________________________________________________
# Module-Manager Daten

class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "list_of_new_sides" : {
            "lucidTag"      : "list_of_new_sides",
            "must_login"    : False,
            "must_admin"    : False,
        },
    }


#_______________________________________________________________________


class ListOfNewSides:
    def __init__( self, PyLucid ):
        #~ self.CGIdata        = PyLucid["CGIdata"]
        self.db             = PyLucid["db"]
        self.config         = PyLucid["config"]
        self.tools          = PyLucid["tools"]

        self.link_url  = '<li>%(date)s - <a href="'
        self.link_url += self.config.system.poormans_url + self.config.system.page_ident
        self.link_url += '%(link)s">%(title)s</a></li>\n'

    def make( self ):
        SQLresult = self.db.select(
            select_items    = [ "id", "name", "title", "lastupdatetime" ],
            from_table      = "pages",
            where           = ( "permitViewPublic", 1 ),
            order           = ( "lastupdatetime", "DESC" ),
            limit           = ( 0, 5 )
        )

        result = '<ul id="ListOfNewSides">'

        for item in SQLresult:
            prelink = self.db.get_page_link_by_id( item["id"] )
            linkTitle   = item["title"]

            if linkTitle == None or linkTitle == "":
                # Eine Seite muß nicht zwingent ein Title haben
                linkTitle = item["name"]

            result += self.link_url % {
                "date"  : self.tools.convert_date_from_sql( item["lastupdatetime"] ),
                "link"  : prelink,# + item["name"],
                "title" : linkTitle,
            }

        result += "</ul>"

        return result



#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid_objects ):
    # Aktion starten
    return ListOfNewSides( PyLucid_objects ).make()


if __name__ == "__main__":
    # Lokaler Test
    from PyLucid_system import SQL, sessiondata
    import config

    db = SQL.db()
    config.readpreferences( db )

    PyLucid = {
        "CGIdata"   : sessiondata.CGIdata( db, config ),
        "db"        : db,
        "config"    : config,
    }
    print ListOfNewSides( PyLucid ).make()
    db.close()












