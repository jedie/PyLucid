#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:sub_menu/>
Generiert das komplette Seitenmenü mit Untermenüs

eingebunden kann es per lucid-"IncludeRemote"-Tag:
<lucidFunction:IncludeRemote>/cgi-bin/PyLucid/Menu.py?page_name=<lucidTag:page_name/></lucidFunction>
"""

__version__="0.2"

__history__="""
v0.2
    - Anpassung an v0.7
v0.1.1
    - Bugfix URLs
v0.1.0
    - Anpassung an neuen ModuleManger
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



from PyLucid.system.BaseModule import PyLucidBaseModule


class sub_menu(PyLucidBaseModule):

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
        """
        Eigentlich keine super tolle Lösung die URL zusammen zu bauen, aber
        effektiv ;)

        mainMenu: {
            'begin': '<ul>', 'finish': '</ul>', 'after': '</li>',
            'currentAfter': '', 'currentBefore': '', 'before': '<li>'
        }
        """
        # List Item Anfang, default: <li>
        self.url_entry  = self.preferences["subMenu"]["before"]
        self.url_entry += '<a href="%(link)s">%(title)s</a>'
        # List Item ende, default: </li>
        self.url_entry += self.preferences["subMenu"]["after"] + "\n"

        current_page_id = self.request.session["page_id"]
        level_prelink = self.db.get_page_link_by_id(current_page_id)

        # List Anfang, default: <ul>
        self.response.write(self.preferences["subMenu"]["begin"] + "\n")

        menu_data = self.db.select(
            select_items    = ["name", "shortcut", "title"],
            from_table      = "pages",
            #~ where           = self.where_filter( [("parent",current_page_id)] ),
            where           = ("parent",current_page_id),
            order           = ("position","ASC")
        )

        for SQLline in menu_data:
            title = SQLline["title"]

            if title == None or title == "":
                title = SQLline["name"]

            linkURL = "%s%s/" % (level_prelink, SQLline["shortcut"])

            self.response.write(
                self.url_entry % {
                    "link"  : linkURL,
                    "title" : cgi.escape(title)
                }
            )

        # List Ende, Default: </ul>
        self.response.write(self.preferences["subMenu"]["finish"] + "\n")
















