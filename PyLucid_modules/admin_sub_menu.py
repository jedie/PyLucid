#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Erzeugt das Administration Sub-Menü
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.0.1"

__history__="""
v0.0.1
    - erste Version
"""

__todo__ = """
"""

# Python-Basis Module einbinden
import sys, cgi



#_______________________________________________________________________
# Module-Manager Daten f�r den page_editor


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
        # Aktion starten
        order = self.CGIdata["command"]
        if order == "admin_sub_menu":
            return self.admin_sub_menu()

    def admin_sub_menu( self ):
        """ Holt das Administration's Sub-Menu aus der DB """
        return self.db.get_internal_page( "admin_sub_menu" )["content"] % {
            "menu" : self.menu_list()
        }

    def menu_list( self ):
        """ Erstellt das admin-sub-Menü """
        menu = ""
        menu_data = self.module_manager.get_menu_data( "admin sub menu" )
        menu = '<ul class="admin_sub_menu">'
        for order,data in menu_data.iteritems():
            menu += '<li><a href="%s?command=%s" title="%s">%s</a></li>' % (
                self.config.system.real_self_url, order, data['txt_long'], data['txt_menu']
            )
        menu += "</ul>"
        return menu

#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid ):
    # Aktion starten
    return admin_sub_menu( PyLucid ).action()




