#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:sub_menu/>
Generiert das komplette Seitenmenü mit Untermenüs

eingebunden kann es per lucid-"IncludeRemote"-Tag:
<lucidFunction:IncludeRemote>/cgi-bin/PyLucid/Menu.py?page_name=<lucidTag:page_name/></lucidFunction>
"""

__version__="0.0.12"

__history__="""
v0.0.12
    - where_filter aus main_menu übernommen, zum beachten von "showlinks" und "permitViewPublic"
v0.0.11
    - Links werden nun richtig mit urllib.quote_plus() behandelt
    - Anpassung an neuen ModuleManager
v0.0.10
    - Zurück auf poormans_url
v0.0.9
    - Seitennamen werden mit cgi.escape() angezeigt.
v0.0.8
    - Aufteilung in menu_sub.py und menu_main.python
    - Tag <lucidTag:sub_menu/> wird über den Modul_Manager gesetzt
v0.0.7
    - Einige Änderung durch neue Seiten-Addressierungs-Umstellung
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

#~ import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import re, os, sys, urllib, cgi





class sub_menu:

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
        #~ self.PyLucid = PyLucid

        self.CGIdata        = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()

        self.db             = PyLucid["db"]

        self.session        = PyLucid["session"]
        #~ self.session.debug()

        self.config         = PyLucid["config"]
        self.preferences    = PyLucid["preferences"]

    def where_filter( self, where_rules ):
        """
        Erweitert das SQL-where Statement um das Rechtemanagement zu berücksichtigen
        selbe funktion ist auch in main_menu vorhanden
        """
        where_rules.append(("showlinks",1))
        if not self.session.has_key("isadmin") or self.session["isadmin"]!=True:
            where_rules.append(("permitViewPublic",1))

        return where_rules

    def lucidTag( self ):
        self.url_entry  = self.preferences["subMenu"]["before"] # List Item Anfang, default: <li>
        self.url_entry += '<a href="%s' % self.link_url
        self.url_entry += '%(link)s">%(title)s</a>'
        self.url_entry += self.preferences["subMenu"]["after"] + "\n"# List Item ende, default: </li>

        current_page_id = self.CGIdata["page_id"]

        level_prelink = self.get_level_prelink( current_page_id )

        #~ mainMenu - {'begin': '<ul>', 'finish': '</ul>', 'after': '</li>', 'currentAfter': '', 'currentBefore': '', 'before': '<li>'}
        # List Anfang, default: <ul>
        print self.preferences["subMenu"]["begin"] + "\n"

        menu_data = self.db.select(
                select_items    = ["name","title"],
                from_table      = "pages",
                where           = self.where_filter( [("parent",current_page_id)] ),
                order           = ("position","ASC")
            )

        for SQLline in menu_data:
            title = SQLline["title"]

            if title == None or title == "":
                title = SQLline["name"]

            print self.url_entry % {
                "link"  : level_prelink + urllib.quote_plus(SQLline["name"]),
                "title" : cgi.escape( title )
            }

        # List Ende, Default: </ul>
        print self.preferences["subMenu"]["finish"] + "\n"


    def get_level_prelink( self, page_id ):
        """ Generiert den prelink für die Absolute-Seiten-Addressierung """
        data = []
        while page_id != 0:
            result = self.db.select(
                    select_items    = ["name","parent"],
                    from_table      = "pages",
                    where           = ("id",page_id)
                )[0]
            page_id  = result["parent"]
            data.append( result["name"] )

        # Liste umdrehen
        data.reverse()

        data = [urllib.quote_plus(i) for i in data]

        return "/%s/" % "/".join(data)
















