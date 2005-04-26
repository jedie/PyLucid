#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert eine horizontale zurück-Linkleiste

Einzubinden über lucid-IncludeRemote-Tag:
<lucidFunction:IncludeRemote>/cgi-bin/PyLucid/BackLinks.py?page_name=<lucidTag:page_name/></lucidFunction>
"""

__version__="0.0.1"

__history__="""
v0.0.2
    - Anpassung an neuer SQL.py Version
v0.0.1
    - erste Version
"""


#~ import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import re, os, sys

print "Content-type: text/html\n"

# Interne PyLucid-Module einbinden
from system import SQL, CGIdata, sessiondata

indexSide = "Start"
indexlink = '<a href="index.php">Index</a>'
backlink = '<a href="?%(name)s">%(title)s</a>'


class backlinks:
    def __init__( self ):
        if not os.environ.has_key("SERVER_SIGNATURE"):
            print "Lokaler Test!"
            current_page_name = "Biografie"
            #~ current_page_name = "ChangeLog"
            print "aktuelle Seite: '%s'" % current_page_name
        else:
            CGIdata.put_in_sessiondata()

            if not sessiondata.cgi.data.has_key("page_name"):
                sys.exit()

            current_page_name = sessiondata.cgi.data["page_name"]

        if current_page_name == indexSide:
            # Die aktuelle Seite ist die Index-Seite, also auch keinen
            # indexLink generieren
            sys.exit()

        self.db = SQL.db()

        # aktuelle parent-ID ermitteln
        parent_id = self.parent_id_by_page_name( current_page_name )

        if parent_id == 0:
            # Keine Unterseite vorhanden -> keine back-Links ;)
            print indexlink
            sys.exit()

        # Für die Link-Daten
        self.data = []

        # Link-Daten aus der DB hohlen und in self.data abspeichern
        self.backlink_data( parent_id )

        # generiert die Link-Leiste
        self.print_links()

    def parent_id_by_page_name( self, page_name ):
        "liefert die parend ID anhand des Namens zur�ck"

        result = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("name",page_name)
            )
        return result[0]["parent"]

    def backlink_data( self, parent_id ):
        "Holt die Links rekursiv von der aktuellen Seite bis zur Index-Seite aus der DB"
        result = self.db.select(
                select_items    = ["name","title","parent"],
                from_table      = "pages",
                where           = ("id",parent_id)
            )
        page_name  = result[0]["name"]
        page_title = result[0]["title"]
        parent_id  = result[0]["parent"]

        if page_title == None:
            # Kein Titel vorhanden, dann nehmen wir den Namen
            page_title = page_name

        link = backlink % {
            "name"  : page_name,
            "title" : page_title
        }

        self.data.append( link )

        if parent_id != 0:
            # Es sind noch unterseiten vorhanden
            self.backlink_data( parent_id )

    def print_links( self ):
        "Links in umgekehrter Reihenfolge ausgeben"

        self.data.append( indexlink )

        self.data.reverse() # Liste umdrehen
        print " &lt; ".join( self.data )


if __name__ == "__main__":
    backlinks()












