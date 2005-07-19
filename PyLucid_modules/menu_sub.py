#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:sub_menu/>
Generiert das komplette Seitenmenü mit Untermenüs

eingebunden kann es per lucid-"IncludeRemote"-Tag:
<lucidFunction:IncludeRemote>/cgi-bin/PyLucid/Menu.py?page_name=<lucidTag:page_name/></lucidFunction>
"""

__version__="0.0.8"

__history__="""
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
import re, os, sys, urllib


# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"


#_______________________________________________________________________
# Module-Manager Daten

class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "sub_menu" : {
            "lucidTag"      : "sub_menu",
            "must_login"    : False,
            "must_admin"    : False,
        },
    }


#_______________________________________________________________________


CSS = { "current" : "current" }
CSStag = ' class="%(style)s"'


class sub_menu:
    def __init__( self, PyLucid ):
        self.PyLucid = PyLucid

        self.CGIdata        = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()

        self.db             = PyLucid["db"]

        self.session        = PyLucid["session"]
        #~ self.session.debug()

        self.config         = PyLucid["config"]
        self.preferences    = PyLucid["preferences"]

        self.link_url  = self.preferences["subMenu"]["before"] # List Item Anfang, default: <li>
        self.link_url += '<a href="'
        self.link_url += self.config.system.poormans_url + self.config.system.page_ident
        self.link_url += '%(link)s">%(title)s</a>'
        self.link_url += self.preferences["subMenu"]["after"] + "\n"# List Item ende, default: </li>

    def generate( self ):
        current_page_id = self.CGIdata["page_id"]

        level_prelink = self.get_level_prelink( current_page_id )

        #~ mainMenu - {'begin': '<ul>', 'finish': '</ul>', 'after': '</li>', 'currentAfter': '', 'currentBefore': '', 'before': '<li>'}
        # List Anfang, default: <ul>
        result = self.preferences["subMenu"]["begin"] + "\n"

        menu_data = self.db.select(
                select_items    = ["name","title"],
                from_table      = "pages",
                where           = ("parent",current_page_id),
                order           = ("position","ASC")
            )

        for SQLline in menu_data:
            title = SQLline["title"]

            if title == None or title == "":
                title = SQLline["name"]

            result += self.link_url % {
                "link"  : urllib.quote( level_prelink + SQLline["name"] ),
                "title" : title
            }

        # List Ende, Default: </ul>
        result += self.preferences["subMenu"]["finish"] + "\n"
        return result

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

        return "/%s/" % "/".join(data)


#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid_objects ):
    # Aktion starten
    return sub_menu( PyLucid_objects ).generate()



if __name__ == "__main__":
    # Aufruf per <lucidFunction:IncludeRemote> vom lucidCMS (also die PHP-Version)
    sys.path.insert( 0, "../" )
    from PyLucid_system import SQL, sessiondata
    import config
    config.system.poormans_url ="X"
    print "Content-type: text/html\n"
    db_handler = SQL.db()
    config.readpreferences( db_handler )
    CGIdata = sessiondata.CGIdata( db_handler )
    MyMG = menugenerator( db_handler, CGIdata, config )
    print MyMG.generate()
    db_handler.close()













