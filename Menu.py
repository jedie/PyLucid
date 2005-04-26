#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert das komplette Seitenmenü mit Untermenüs

eingebunden kann es per lucid-"IncludeRemote"-Tag:
<lucidFunction:IncludeRemote>/cgi-bin/PyLucid/Menu.py?page_name=<lucidTag:page_name/></lucidFunction>
"""

__version__="0.0.1"

__history__="""
v0.0.1
    - erste Version
"""


#~ import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import re, os, sys

print "Content-type: text/html\n"

# Interne PyLucid-Module einbinden
from system import SQL, CGIdata, sessiondata


CSS = { "current" : "current" }
CSStag = ' class="%(style)s"'
menulink = '%(space)s<li><a%(style)s href="?%(name)s">%(title)s</a></li>'


class menugenerator:
    def __init__( self ):
        if not os.environ.has_key("SERVER_SIGNATURE"):
            print ">>> Lokaler Test!"
            #~ current_page_name = "Biografie"
            current_page_name = "Filmtheorie"
            #~ current_page_name = "Start"
            print "-aktuelle Seite: '%s'" % current_page_name
        else:
            CGIdata.put_in_sessiondata()

            if not sessiondata.cgi.data.has_key("page_name"):
                sys.exit()

            current_page_name = sessiondata.cgi.data["page_name"]

        self.db = SQL.db()

        # "Startpunkt" für die Menügenerierung feststellen
        parentID = self.get_parentID( current_page_name )

        # Wird von self.create_menudata() "befüllt"
        self.menudata = []

        # Füllt self.menudata mit allen relevanten Daten
        self.create_menudata( parentID )

        # Ebenen umdrehen, damit das Menü auch richtig rum dargestellt werden kann
        self.menudata.reverse()

        # Generiert das Menü aus self.menudata
        self.print_menu()


    def get_parentID( self, page_name ):
        """
        liefert die parend ID anhand des Namens zur�ck
        dies ist quasi Startpunkt zur Menügenerierung.

        Damit sich das evtl. vorhandene Untermenüpunkt "aufklappt" wird
        nachgesehen ob ein Menüpunkt als ParentID die aktuelle SeitenID hat.
        """
        # Anhand des Seitennamens wird die aktuelle SeitenID und den ParentID ermittelt
        result = self.db.select(
                select_items    = ["id","parent"],
                from_table      = "pages",
                where           = ("name",page_name)
            )
        self.current_page_id = result[0]["id"]
        page_parentID = result[0]["parent"]

        # Gibt es Untermenupunkte?
        result = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("parent",self.current_page_id),
                limit           = (0,1)
            )
        if result == []:
            # Es gibt keine höhere Ebene (keine Untermenupunkte)
            return page_parentID
        else:
            # Als startpunkt wird die ParentID eines Untermenupunktes übergeben
            return result[0]["parent"]

    def create_menudata( self, parentID ):
        """
        Hohlt die relevanten Menüdaten aus der DB in einer Rekursiven-Schleife
        """

        # Alle Daten des aktuellen Ebene hohlen
        parents = self.db.select(
                select_items    = ["id","name","title","parent"],
                from_table      = "pages",
                where           = [ ("parent",parentID), ("permitViewPublic",1) ],
                order           = ("position","ASC")
            )
        self.menudata.append( parents )
        #~ self.db.dump_select_result( parents )
        #~ print "-"*80

        # Hohlt die parentID, um zur nächte Ebene zurück gehen zu können
        parent = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("id",parentID)
            )
        if parent != []:
            # Unterste Ebene noch nicht erreicht -> rekursiver Aufruf
            self.create_menudata( parent[0]["parent"] )

    def print_menu( self, menulevel=0 ):
        """
        Erstellt das Menü aus self.menudata in einer Rekursiven-Schleife
        """
        # Daten der Aktuellen Menüebene
        leveldata = self.menudata[ menulevel ]

        if len(self.menudata) > (menulevel+1):
            # Es gibt noch eine höhere Menu-Ebene
            higher_level_parent = self.menudata[ menulevel+1 ][0]["parent"]
        else:
            # Es gibt keine höhere Ebene
            higher_level_parent = False

        # Leerzeichen für das einrücken des HTML-Code
        spacer = " " * (menulevel * 2)

        print spacer + "<ul>"

        for menuitem in leveldata:
            name = menuitem["name"]
            title = menuitem["title"]
            if title == None:
                title = name

            if menuitem["id"] == self.current_page_id:
                # Der aktuelle Menüpunkt ist der "angeklickte"
                CSS_style_tag = CSStag % {
                        "style" : CSS["current"]
                    }
            else:
                CSS_style_tag = ""

            print menulink % {
                    "space" : spacer*2,
                    "style" : CSS_style_tag,
                    "name"  : name,
                    "title" : title
                }

            if higher_level_parent != False:
                # Generell gibt es noch eine höhere Ebene

                if menuitem["id"] == higher_level_parent:
                    # Es wurde der Menüpunkt erreicht, der das Untermenü "enthält",
                    # deswegen kommt ab hier erstmal das Untermenü rein
                    self.print_menu( menulevel+1 )

        print spacer + "</ul>"



if __name__ == "__main__":
    menugenerator()












