#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert das komplette Seitenmenü mit Untermenüs

eingebunden kann es per lucid-"IncludeRemote"-Tag:
<lucidFunction:IncludeRemote>/cgi-bin/PyLucid/Menu.py?page_name=<lucidTag:page_name/></lucidFunction>
"""

__version__="0.0.6"

__history__="""
v0.0.6
    - neu: sub_menu()
    - es werden <ul>,<li> usw. aus der DB (preferences) genommen
v0.0.5
    - Anpassung an index.py (Rendern der CMS-Seiten mit Python'CGIs)
    - SQL-Connection wird nun auch beendet
v0.0.4
    - Umstellung: Neue Handhabung der CGI-Daten
v0.0.3
	- Fehlerausgabe bei unbekannter 'page_name'
v0.0.2
    - Menulink mit 'title' erweitert, Link-Text ist nun 'name'
v0.0.1
    - erste Version
"""

import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import re, os, sys


# Interne PyLucid-Module einbinden
#~ from system import SQL, sessiondata, config
#~ from system import config



CSS = { "current" : "current" }
CSStag = ' class="%(style)s"'


class menugenerator:
    def __init__( self, db_handler, CGIdata_class, config, sessionhandler="" ):
        self.db         = db_handler
        self.CGIdata    = CGIdata_class
        self.session    = sessionhandler
        self.config     = config

        self.menulink  = '%(space)s'
        # List item Start, default: <li>
        self.menulink += self.config.preferences["mainMenu"]["before"]
        self.menulink += '<a%(style)s href="'
        self.menulink += config.system.poormans_url
        self.menulink += '?%(name)s" title="%(title)s">%(name)s</a>'
        # List item Ende, default: </li>
        self.menulink += self.config.preferences["mainMenu"]["after"]

        self.current_page_name  = self.CGIdata["page_name"]
        self.current_page_id    = self.db.side_id_by_name( self.current_page_name )

        # Wird von self.create_menudata() "befüllt"
        self.menudata = []

    def generate( self ):
        # "Startpunkt" für die Menügenerierung feststellen
        parentID = self.db.parentID_by_name( self.current_page_name )
        # Gibt es Untermenupunkte?
        parentID = self.check_submenu( parentID )

        # Füllt self.menudata mit allen relevanten Daten
        self.create_menudata( parentID )

        # Ebenen umdrehen, damit das Menü auch richtig rum dargestellt werden kann
        self.menudata.reverse()

        # Generiert das Menü aus self.menudata
        return self.make_menu()

    def check_submenu( self, parentID, internal=False ):
        """
        Damit sich das evtl. vorhandene Untermenüpunkt "aufklappt" wird
        nachgesehen ob ein Menüpunkt als ParentID die aktuelle SeitenID hat.
        """
        # Gibt es Untermenupunkte?
        result = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = [ ("parent",self.current_page_id), ("permitViewPublic",1) ],
                limit           = (0,1)
            )
        if result == []:
            # Es gibt keine hÃ¶here Ebene (keine Untermenupunkte)
            return parentID
        else:
            # Als startpunkt wird die ParentID eines Untermenupunktes übergeben
            return result[0]["parent"]

    def create_menudata( self, parentID, internal=False ):
        """
        Hohlt die relevanten Menüdaten aus der DB in einer Rekursiven-Schleife
        """
        # Alle Daten der aktuellen Ebene hohlen
        parents = self.db.select(
                select_items    = ["id","name","title","parent"],
                from_table      = "pages",
                where           = [ ("parent",parentID), ("permitViewPublic",1) ],
                order           = ("position","ASC")
            )
        self.menudata.append( parents )

        # Hohlt die parentID, um zur nÃ¤chte Ebene zurück gehen zu kÃ¶nnen
        parent = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = [ ("id",parentID) ]
            )
        if parent != []:
            # Unterste Ebene noch nicht erreicht -> rekursiver Aufruf
            self.create_menudata( parent[0]["parent"] )

    def make_menu( self, menulevel=0 ):
        """
        Erstellt das Menü aus self.menudata in einer Rekursiven-Schleife
        """
        # Daten der Aktuellen Menüebene
        leveldata = self.menudata[ menulevel ]

        if len(self.menudata) > (menulevel+1):
            # Es gibt noch eine hÃ¶here Menu-Ebene
            higher_level_parent = self.menudata[ menulevel+1 ][0]["parent"]
        else:
            # Es gibt keine hÃ¶here Ebene
            higher_level_parent = False

        # Leerzeichen für das einrücken des HTML-Code
        spacer = " " * (menulevel * 2)

        #~ mainMenu - {'begin': '<ul>', 'finish': '</ul>', 'after': '</li>', 'currentAfter': '', 'currentBefore': '', 'before': '<li>'}
        # List Anfang, default: <ul>
        result = spacer + self.config.preferences["mainMenu"]["begin"] + "\n"

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

            result += self.menulink % {
                    "space" : spacer*2,
                    "style" : CSS_style_tag,
                    "name"  : name,
                    "title" : title
                }
            result += "\n"

            if higher_level_parent != False:
                # Generell gibt es noch eine hÃ¶here Ebene

                if menuitem["id"] == higher_level_parent:
                    # Es wurde der Menüpunkt erreicht, der das Untermenü "enthÃ¤lt",
                    # deswegen kommt ab hier erstmal das Untermenü rein
                    result += self.make_menu( menulevel+1 )

        #~ mainMenu - {'begin': '<ul>', 'finish': '</ul>', 'after': '</li>', 'currentAfter': '', 'currentBefore': '', 'before': '<li>'}
        # List Ende, default: </ul>
        result += spacer + self.config.preferences["mainMenu"]["finish"] + "\n"

        return result



class sub_menu:
    def __init__( self, db_handler, CGIdata_class, config ):
        self.db         = db_handler
        self.CGIdata    = CGIdata_class
        #~ self.CGIdata.debug()
        self.config     = config
        #~ self.config.debug()

    def generate( self ):
        current_page_id = self.CGIdata["page_id"]

        #~ mainMenu - {'begin': '<ul>', 'finish': '</ul>', 'after': '</li>', 'currentAfter': '', 'currentBefore': '', 'before': '<li>'}
        # List Anfang, default: <ul>
        result = self.config.preferences["subMenu"]["begin"] + "\n"

        menu_data = self.db.select(
                select_items    = ["name","title"],
                from_table      = "pages",
                where           = ("parent",current_page_id),
                order           = ("position","ASC")
            )

        # List Item Anfang, default: <li>
        before = self.config.preferences["subMenu"]["before"]
        # List Item ende, default: </li>
        after = self.config.preferences["subMenu"]["after"] + "\n"

        for SQLline in menu_data:
            name = SQLline["name"]
            title = SQLline["title"]

            if title == None or title == "":
                title = name

            result += '%s<a href="%s?%s">%s</a>%s' % (
                before,
                self.config.system.poormans_url,
                name,
                title,
                after
                )

        # List Ende, Default: </ul>
        result += self.config.preferences["subMenu"]["finish"] + "\n"
        return result






if __name__ == "__main__":
    # Aufruf per <lucidFunction:IncludeRemote> vom lucidCMS (also die PHP-Version)
    print "Content-type: text/html\n"
    db_handler = SQL.db()
    CGIdata = sessiondata.CGIdata()
    MyMG = menugenerator( db_handler, CGIdata )
    print MyMG.generate()
    db_handler.close()













