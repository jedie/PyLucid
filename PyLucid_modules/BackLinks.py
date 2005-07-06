#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert eine horizontale zurück-Linkleiste

Einzubinden über lucid-IncludeRemote-Tag:
<p id=Backlinks>
<lucidFunction:IncludeRemote>/cgi-bin/PyLucid/BackLinks.py?page_name=<lucidTag:page_name/></lucidFunction>
</p>
"""

__version__="0.0.4"

__history__="""
v0.0.4
    - Anpassung an index.py (Rendern der CMS-Seiten mit Python'CGIs)
    - Umstellung: Neue Handhabung der CGI-Daten
    - SQL-Connection wird nun auch beendet
v0.0.3
    - Links werden statt mit print mit sys.stdout.write() geschrieben, damit kein Zeilenumbruch vorkommt
v0.0.2
    - Anpassung an neuer SQL.py Version
v0.0.1
    - erste Version
"""


import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import re, os, sys

# Interne PyLucid-Module einbinden
#~ from system import SQL, sessiondata

indexSide = "Start"
indexlink = '<a href="/">Index</a>'
backlink = '<a href="?%(name)s">%(title)s</a>'


class backlinks:
    def __init__( self, db_handler, current_page_name ):
        self.db                 = db_handler
        self.current_page_name  = current_page_name

        # Für die Link-Daten
        self.data = []

    def make( self ):
        "Backlinks generieren"
        if self.current_page_name == indexSide:
            # Die aktuelle Seite ist die Index-Seite, also auch keinen
            # indexLink generieren
            return ""

        # aktuelle parent-ID ermitteln
        parent_id = self.parent_id_by_page_name( self.current_page_name )

        if parent_id == 0:
            # Keine Unterseite vorhanden -> keine back-Links ;)
            return indexlink

        # Link-Daten aus der DB hohlen und in self.data abspeichern
        self.backlink_data( parent_id )

        # Am Ende den Link zum Index anfügen
        self.data.append( indexlink )

        # Liste umdrehen
        self.data.reverse()

        return " &lt; ".join( self.data )


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



if __name__ == "__main__":
    # Aufruf per <lucidFunction:IncludeRemote>
    print "Content-type: text/html\n"
    db_handler = SQL.db()
    CGIdata = sessiondata.CGIdata()
    current_page_name = CGIdata["page_name"]
    print backlinks( db_handler, current_page_name ).make()
    db_handler.close()












