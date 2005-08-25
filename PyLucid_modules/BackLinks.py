#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:back_links/>
Generiert eine horizontale zurück-Linkleiste

Einzubinden über lucid-IncludeRemote-Tag:
<p id=Backlinks>
<lucidFunction:IncludeRemote>/cgi-bin/PyLucid/BackLinks.py?page_name=<lucidTag:page_name/></lucidFunction>
</p>
"""

__version__="0.0.7"

__history__="""
v0.0.7
    - Index-Link war falsch
v0.0.6
    - Tag <lucidTag:back_links/> über Modul-Manager
v0.0.5
    - Fast ganz neu geschrieben, durch Seiten-Addressierungs-Umstellung
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

indexSide = "Start"

#_______________________________________________________________________
# Module-Manager Daten

class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "back_links" : {
            "lucidTag"      : "back_links",
            "must_login"    : False,
            "must_admin"    : False,
        },
    }


#_______________________________________________________________________

class backlinks:
    def __init__( self, PyLucid ):
        self.CGIdata        = PyLucid["CGIdata"]
        self.db             = PyLucid["db"]
        self.config         = PyLucid["config"]
        self.preferences    = PyLucid["preferences"]

        self.indexlink = '<a href="%s">Index</a>' % (
            self.config.system.poormans_url + self.config.system.page_ident
        )

        self.backlink  = '<a href="'
        self.backlink += self.config.system.poormans_url + self.config.system.page_ident
        self.backlink += '%(url)s">%(title)s</a>'

        #~ self.config.debug()
        self.current_page_id  = self.CGIdata["page_id"]

    def make( self ):
        "Backlinks generieren"
        if self.current_page_id == self.preferences["core"]["defaultPageName"]:
            # Die aktuelle Seite ist die Index-Seite, also auch keinen
            # indexLink generieren
            return ""

        # aktuelle parent-ID ermitteln
        parent_id = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("id",self.current_page_id)
            )[0]["parent"]

        if parent_id == 0:
            # Keine Unterseite vorhanden -> keine back-Links ;)
            return self.indexlink

        # Link-Daten aus der DB hohlen
        data = self.backlink_data( parent_id )

        return self.make_links( data )

    def backlink_data( self, page_id ):
        """ Holt die Links von der aktuellen Seite bis zur Index-Seite aus der DB """
        data = []
        while page_id != 0:
            result = self.db.select(
                    select_items    = ["name","title","parent"],
                    from_table      = "pages",
                    where           = ("id",page_id)
                )[0]
            page_id  = result["parent"]
            data.append( result )

        # Liste umdrehen
        data.reverse()

        return data

    def make_links( self, data ):
        """ Generiert aus den Daten eine Link-Zeile """
        links = self.indexlink
        oldurl = ""
        for link_data in data:
            url = oldurl + "/" + link_data["name"]
            oldurl = url

            title = link_data["title"]
            if title == None or title == "":
                title = link_data["name"]

            links += " &lt; " + self.backlink % {
                "url": url,
                "title": title,
            }

        return links


#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid_objects ):
    # Aktion starten
    return backlinks( PyLucid_objects ).make()



if __name__ == "__main__":
    # Lokaler Test
    sys.path.insert( 0, "../" )
    from PyLucid_system import SQL, sessiondata
    import config

    db = SQL.db()
    config.readpreferences( db )

    PyLucid = {
        "CGIdata"   : sessiondata.CGIdata( db, config ),
        "db"        : db,
        "config"    : config,
    }
    print backlinks( PyLucid ).make()
    db.close()












