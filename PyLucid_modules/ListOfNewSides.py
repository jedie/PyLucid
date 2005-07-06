#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert eine Liste der "letzten Änderungen"
"""

__version__="0.0.4"

__history__="""
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


# Interne PyLucid-Module einbinden
#~ from system import config, lucid_tools
from PyLucid_system import lucid_tools

class ListOfNewSides:
    def __init__( self, db_handler ):
        self.db = db_handler

    def make( self ):
        SQLresult = self.db.select(
            select_items    = [ "title", "name", "lastupdatetime" ],
            from_table      = "pages",
            where           = ( "permitViewPublic", 1 ),
            order           = ( "lastupdatetime", "DESC" ),
            limit           = ( 0, 5 )
        )

        result = '<ul id="ListOfNewSides">'

        for item in SQLresult:
            linkTitle   = item["title"]
            linkName    = item["name"]

            if linkTitle == None or linkTitle == "":
                # Eine Seite muß nicht zwingent ein Title haben
                linkTitle = item["name"]

            line = '%(date)s - <a href="?%(Name)s">%(Title)s</a>' % {
                "Name"  : linkName,
                "Title" : linkTitle,
                "date"  : lucid_tools.date( item["lastupdatetime"] )
            }
            result += "<li>%s</li>" % line

        result += "</ul>"

        return result

def start( db_handler ):
    # ist noch per IncludeRemote eingebunden, wird aber von PyLucid als
    # lokales Skript erkannt und per import "gestartet"
    return ListOfNewSides( db_handler ).make()


if __name__ == "__main__":
    # Aufruf per <lucidFunction:IncludeRemote>
    print "Content-type: text/html\n"
    from system import SQL
    db_handler = SQL.db()
    print ListOfNewSides( db_handler ).make()
    db_handler.close()












