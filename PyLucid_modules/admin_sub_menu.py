#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

"""
Erzeugt das Administration Sub-Menü
"""

__version__="0.0.2"

__history__="""
v0.0.2
    - Umbau, damit die Kategorieren in den Modulen beachtet werden
    - Nun wird auch normale mit print die Ergebnisse ausgegeben
v0.0.1
    - erste Version
"""

__todo__ = """
Irgendwie sollte die Reihenfolge der Modul-Kategorieren vom Admin festgelegt
werden können, aber wie?
"""

# Python-Basis Module einbinden
import sys, cgi



#_______________________________________________________________________
# Module-Manager Daten für den page_editor


class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "admin_sub_menu" : {
            "txt_menu"      : "sub menu",
            "txt_long"      : "goto administration sub menu",
            "section"       : "front menu",
            "must_login"    : True,
            "must_admin"    : True,
        },
    }


#_______________________________________________________________________


class admin_sub_menu:
    def __init__( self, PyLucid ):
        self.CGIdata        = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.db             = PyLucid["db"]
        self.page_msg       = PyLucid["page_msg"]
        self.config         = PyLucid["config"]
        self.module_manager = PyLucid["module_manager"]

    def action( self ):
        if self.CGIdata["command"] != "admin_sub_menu":
            print "Error: command '%s' unknown!" % cgi.escape( self.CGIdata["command"] )
            return

        # Moduldaten vom Module-manager holen
        menu_data = self.module_manager.get_menu_data( "admin sub menu" )

        # Moduldaten nach Kategorieren ordnen
        menu_data = self._menudata_by_category( menu_data )

        # HTML-Liste erzeugen
        menu_data = self._generate_menu( menu_data )

        # In Template einfügen und ausgeben
        print self.db.get_internal_page( "admin_sub_menu" )["content"] % {
            "menu" : menu_data
        }

    def _menudata_by_category( self, menu_data ):
        """
        Sortiert die Menüdaten nach den angegebenen Kategorieren und erstellt
        für denen Eintrage die komplette HTML-Zeile
        Zurückgegeben wird ein Dict.
        """
        data_by_category = {}
        for order,data in menu_data.iteritems():
            listitem = '<li><a href="%s?command=%s" title="%s">%s</a></li>' % (
                self.config.system.real_self_url, order, data['txt_long'], data['txt_menu']
            )
            try:
                data['category']
            except KeyError:
                # Es ist keine category der module_info-Pseudo-Klasse angegeben
                data['category'] = "[undefined]"

            try:
                data_by_category[data['category']].append( listitem )
            except KeyError:
                data_by_category[data['category']] = [ listitem ]

        return data_by_category

    def _generate_menu( self, data_by_category ):
        """
        Erstellt aus den Daten die HTML-Listen
        """
        menu = ""
        for category, listitems in data_by_category.iteritems():
            menu += '<h3 class="admin_sub_menu">%s</h1>' % category
            menu += '<ul class="admin_sub_menu">'
            for listitem in listitems:
                menu += listitem
            menu += "</ul>"
        return menu

#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid ):
    # Aktion starten
    admin_sub_menu( PyLucid ).action()




