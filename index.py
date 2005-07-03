#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Rendert eine komplette Seite

Information zu Userverwaltung
-----------------------------

Offentlich zu sehende Seiten haben ein permitViewPublic = 1


    Interne PyLucid-Seiten
    ----------------------
Damit PyLucid-Internen Seiten (z.B. Login-Formular) von normalen Seiten
unterschieden werden können, gibt es eine User-Gruppe "PyLucid_internal".
Interne PyLucid Seiten haben ein ownerID == id("PyLucid_internal")


    Allgemeine Seiteneigenschaften
    ------------------------------
showlinks           -
permitViewPublic    - Gruppe die die Seite sehen dürfen
permitViewGroupID   -
ownerID             - ID des Erstellers
lastupdateby        - ID des Users der die Seite zuletzt verändert hat
permitEditGroupID   - Gruppe die die Seite verändern dürfen

"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.2.0"

__history__="""
v0.2.0
    - einige Umstellungen/Bugfixes
    - LogIn, PageEdit fertig
v0.1.0
    - erste Version
"""

__todo__ = """
Mehrfach-connection zur SQL-DB vermeiden und SQL.close() nicht vergessen:
    preferences.py
        Dringende Überarbeitung, wegen eigenständiger DB-Connection!

lucidTag_page_style_link
    lifert nicht den CSS-Links, sondern bettet CSS ein!

rendern:
    Zum beschleunigten Seitenaufbau, sollten alle Teilergebnisse der Seite direkt
    per print rausgeschrieben werden.
"""

__info__ = """<a href="http://www.jensdiemer.de/?PyLucid">PyLucid v%s</a>""" % __version__


# Als erstes Mal die Zeit stoppen ;)
import time
start_time = time.time()

import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import os, sys

# Interne PyLucid-Module einbinden
from system import SQL, sessiondata, sessionhandling, config
from system import lucid_tools, userhandling, SQL_logging, pagerender

pagerender.__info__ = __info__ # Versions-Information übertragen

## Dynamisch geladene Module:
## urllib2 -> LucidRender.lucidFunction_IncludeRemote()



#~ import cgi

#~ cgi.print_arguments()
#~ cgi.print_directory()
#~ cgi.print_environ()
#~ cgi.print_environ_usage()
#~ cgi.print_exception()


save_max_history_entries = 10


class LucidRender:
    def __init__( self ):
        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.db             = SQL.db()

        # lucid Einstellungen aus DB lesen
        config.readpreferences( self.db )

        # CGI Post/Get Daten
        self.CGIdata        = sessiondata.CGIdata( self.db )
        #~ self.CGIdata.debug()

        # Log-Ausgaben in SQL-DB
        self.log            = SQL_logging.log( self.db.cursor )
        self.log.set_typ("index.py")

        # Session Daten gebunden an den User
        self.session        = sessionhandling.sessionhandler( self.db.cursor, "lucid_session_data", self.log )

        # Userverwaltung: LogIn/LogOut
        self.auth           = userhandling.auth( self.db, self.log, self.CGIdata, self.session )

        # Zum zusammenbau der HTML-Seiten
        self.pagerender     = pagerender.pagerender( self.session, self.CGIdata, self.db, self.auth )

    def save_page_history( self ):
        """
        Der User ist eingeloggt -> folgende Informationen werden gespeichert
            session["page_history"]: History der Besuchten Seiten
        """
        history = []
        if self.session.has_key("page_history"):
            # Es wurden schon Seiten besucht
            history = self.session["page_history"]
            if len(history)>save_max_history_entries:
                # History kürzen ;)
                history = history[:save_max_history_entries]

        # Fügt die aktuelle Seite am Anfang der Liste ein
        history.insert( 0, self.CGIdata["page_id"] )

        # Speichert die aktuell besuchte Seite
        self.session["page_history"] = history


    def make( self ):
        "Baut die Seite zusammen und liefert sie zurÃ¼ck"
        if self.CGIdata.has_key("command"):
            # Ein Kommando soll ausgefÃ¼hrt werden
            content = self.command( self.CGIdata["command"] )

            if self.session.has_key("page_history"):
                self.CGIdata["page_id"]     = self.session["page_history"][0]
            else:
                self.CGIdata.set_default_page()

            self.CGIdata["page_name"]   = self.db.side_name_by_id( self.CGIdata["page_id"] )
            # Information der Seite aus DB holen
            side_data = self.db.get_page_data( self.CGIdata["page_id"] )
        else:
            if self.session.ID != False:
                # User ist eingeloggt -> Es werden Informationen gespeichert.
                self.save_page_history()

            # Information der Seite aus DB holen
            side_data = self.db.get_page_data( self.CGIdata["page_id"] )

            if self.CGIdata.page_name_error:
                # Seite existiert nicht
                content = "<h1>Error!</h1><h3>Page not found!</h3>"
            else:
                # Parsen des SeitenInhalt, der Aufgerufenen Seite
                content = self.pagerender.lucidTag_page_body( side_data )

        if type(content) != str:
            # Mit dem Inhalt stimmt was nicht!
            content = "<h1>Internal Contenttyp error (not String)!</h1><br/>Content:<hr/>" + str( content )

        if self.session.ID != False:
            # User ist eingeloggt -> Einblenden des Admin-MenÃ¼'s
            content = self.pagerender.admin_menu() + content

        # Parsen das Templates
        template = self.pagerender.replace_lucidTags( side_data["template"], side_data )

        #############################
        ## Die Arbeit ist erledigt ;)
        #############################

        # Sessiondaten in die Datenbank schreiben
        self.session.update_session()
        # Datenbank verbindung beenden
        self.db.close()

        # SeitenInhalt in Template einfÃ¼gen
        try:
            content = template.replace( "<lucidTag:page_body/>", content )
        except Exception, e:
            content = "Page Content Error: '%s'<hr>content:<br />%s" % (e, content)

        return content.replace( "<lucidTag:script_duration/>", "%.2f" % (time.time() - start_time) )



    ####################################################
    # Spezialitäten

    def command( self, order ):
        #~ print "Content-type: text/html\n"
        #~ print "<pre>"
        #~ for k,v in self.CGIdata.iteritems(): print "%s - %s" % (k,v)
        #~ print "</pre>"
        #~ sys.exit()

        self.log( "Special PyLuid command: '%s'" % order )
        if order == "login":
            # Der User will einloggen
            return self.auth.make_login_page()
        elif order == "logout":
            return self.auth.logout()
        elif order == "check_login":
            return self.auth.check_login()
        elif order =="edit_page":
            if self.session.ID == False:
                return "<h1>ERROR!<h1><h2>Your not login!</h2>"
            from system import pageadmin
            return pageadmin.page_editor( self.CGIdata, self.session, self.db, self.auth ).get()
        else:
            return "<h1>ERROR!</h1><br/>Command unknow!"



if __name__ == "__main__":
    #~ print "Content-type: text/html\n"
    MyLR = LucidRender()
    page_content = MyLR.make()
    print "Content-type: text/html\n"
    print page_content
