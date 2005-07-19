#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)



#~ import sys

#~ from PyLucid_modules.user_auth import module_info
#~ help(module_info)
#~ print "-"*80

#~ from PyLucid_system import module_manager
#~ module_manager = module_manager.module_manager()
#~ module_manager.read_module_info( "PyLucid_modules" )
#~ module_manager.debug()
#~ print module_manager.get_orders()
#~ print module_manager.get_front_menu()
#~ sys.exit()



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


    Module-Manager
    --------------
Der Modul-Manager ist für Module/Plugins zuständig. In den jeweiligen
Modulen/Plugins muß die Pseudoklasse "module_info" existieren. In dieser
Klasse werden Informationen über das Module/Plugin festgehalten, die vom
Module-Manager eingelesen werden und PyLucid zur ferfügung gestellt werden.
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"
__url__ = "http://www.jensdiemer.de/Programmieren/Python/PyLucid"

__version__="0.2.8"

__history__="""
v0.2.8
    - aus sessiondata.py die detect_page Funktion nach hierhin verlagert
v0.2.7
    - Weite Teile von .command() in den Module-Manager ausgelagert
v0.2.6
    - Seiten-Addressierungs-Umstellung: Nun ist es auch endlich möglich zwei
        Seiten mit gleichen Namen zu haben, weil es nun immer ein
        "Absoluten"-Pfad gibt.
v0.2.5
    - NEU: Administration-Sub-Menu:
        Editieren von Stylesheets, Templates und internen-Seiten!
v0.2.4
    - Auch aus den command-Ergebnissen, werden alle Tag's ersetzt.
        z.B. für den Preview beim Seiten editieren
    - NEU: Modul-Manager: "./PyLucid_system/module_manager.py"
    - Umstellung für user_auth.py und pageadmin.py, diese werden jetzt
        über den Modul-Manager "eingebunden".
v0.2.3
    - Komplette Verzeichnis-Struktur Umstellung:
        ./index.py          - Index-Datei
        ./config.py         - Konfigurationsdatei
        ./PyLucid_CSS       - CSS-Datei-Cache (noch unfertig!)
        ./PyLucid_JS        - JavaScripte für's MD5-Login
        ./PyLucid_modules   - Eingebaute Erweiterungen (Menu,ListOfNewSides usw.)
        ./PyLucid_system    - Grundlegende System Module
v0.2.1
    - keywords und description werden nun endlich eingefügt ;)
v0.2.0
    - einige Umstellungen/Bugfixes
    - LogIn, PageEdit fertig
v0.1.0
    - erste Version
"""

__todo__ = """

 * Fehler bei abgelaufener Session!
 * Sicherheit: neue Seiten können auch nicht Admins anlegen...

lucidTag_page_style_link
    lifert nicht den CSS-Links, sondern bettet CSS ein!

rendern:
    Zum beschleunigten Seitenaufbau, sollten alle Teilergebnisse der Seite direkt
    per print rausgeschrieben werden.
"""

__info__ = """<a href="%s">PyLucid v%s</a>""" % (__url__,__version__)


# Als erstes Mal die Zeit stoppen ;)
import time
start_time = time.time()

import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import os, sys, urllib

# Interne PyLucid-Module einbinden
import config # PyLucid Konfiguration
from PyLucid_system import SQL, sessiondata, sessionhandling
from PyLucid_system import userhandling, SQL_logging, pagerender
from PyLucid_system import module_manager, tools, preferences


pagerender.__info__ = __info__ # Versions-Information übertragen

## Dynamisch geladene Module:
## urllib2 -> LucidRender.lucidFunction_IncludeRemote()



#~ import cgi

#~ cgi.print_arguments()
#~ cgi.print_directory()
#~ cgi.print_environ()
#~ cgi.print_environ_usage()
#~ cgi.print_exception()

#~ print "Content-type: text/html\n"

save_max_history_entries = 10


class LucidRender:
    def __init__( self ):
        # Alle Objekte/Klassen, die für Module/Plugins nötig sein könnten, werden
        # in dem Dict PyLucid_objects abgelegt. Dieses erlaubt ein vereinheitliche
        # Instanzierung von Modulen
        self.PyLucid = {}

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.page_msg       = sessiondata.page_msg()
        self.PyLucid["page_msg"] = self.page_msg

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.db             = SQL.db()
        self.PyLucid["db"] = self.db

        # Verwaltung für Einstellungen aus der Datenbank
        self.preferences    = preferences.preferences( self.PyLucid )
        self.PyLucid["preferences"] = self.preferences

        # PyLucid's Konfiguration
        self.config         = config
        self.PyLucid["config"] = self.config

        tools.PyLucid = self.PyLucid
        self.PyLucid["tools"] = tools

        # CGI Post/Get Daten
        self.CGIdata        = sessiondata.CGIdata( self.PyLucid )
        #~ self.CGIdata.debug()
        self.PyLucid["CGIdata"] = self.CGIdata

        # Log-Ausgaben in SQL-DB
        self.log            = SQL_logging.log( self.PyLucid )
        self.PyLucid["log"] = self.log

        # Allgemeiner CGI Sessionhandler auf mySQL-Basis
        self.session        = sessionhandling.sessionhandler(
            self.db.cursor, "lucid_session_data", self.log,
            CookieName="PyLucid_id"
        )
        #~ self.session.debug()
        self.PyLucid["session"] = self.session

        # Für die Log-Einträge Informationen festhalten
        self.log.client_sID         = self.session.ID
        if self.session.has_key("user"):
            self.log.client_user_name   = self.session["user"]

        # Verwaltung von erweiterungs Modulen/Plugins
        self.module_manager = module_manager.module_manager( self.PyLucid )
        # Alle Module, die für den Modul-Manager vorbereitet wurden einlesen
        self.module_manager.read_module_info( "PyLucid_modules" )
        #~ self.module_manager.debug()
        self.PyLucid["module_manager"] = self.module_manager

        # Zum Zusammenbau der HTML-Seiten
        self.pagerender     = pagerender.pagerender( self.PyLucid )

    #_____________________________________________________________________________________________________

    def make( self ):
        "Baut die Seite zusammen und liefert sie zurück"

        # Aktuelle Seite ermitteln und festlegen
        self.detect_page()

        if self.CGIdata.has_key("command"):
            # Ein Kommando soll ausgeführt werden
            module_content = self.command( self.CGIdata["command"] )
        else:
            module_content = None

        # Information der Seite aus DB holen
        try:
            side_data = self.db.get_side_data( self.CGIdata["page_id"] )
        except IndexError, e:
            self.error( "Can get Page:", e, "page_id:", self.CGIdata["page_id"] )

        if module_content != None:
            #~ self.page_msg( "module_content:",module_content )
            # Das Modul selber hat eine Seite erzeugt, die Angezeigt werden soll
            if type( module_content ) == tuple:
                side_data["content"]    = module_content[0]
                side_data["markup"]     = module_content[1]
            else:
                # Einfacher rückgabe der Daten -> Markup ist immer none
                side_data["content"]    = module_content
                side_data["markup"]     = "none"

        #~ self.page_msg( "Markup:",side_data["markup"] )
        return self.build_side( side_data )


    def build_side( self, side_data ):

        # Parsen des SeitenInhalt, der Aufgerufenen Seite
        main_content = self.pagerender.lucidTag_page_body( side_data )

        #~ self.page_msg( main_content )

        if type(main_content) != str:
            # Mit dem Inhalt stimmt was nicht!
            main_content = "<h1>Internal contenttyp error (not String)!</h1><br/>Content:<hr/>" + str( main_content )

        if self.session.ID != False:
            # User ist eingeloggt -> Es werden Informationen gespeichert.
            self.save_page_history()

            # Einblenden des Admin-Menü's
            main_content = self.pagerender.admin_menu() + main_content

        # Parsen das Templates
        template = self.pagerender.replace_lucidTags( side_data["template"], side_data )

        #############################
        ## Die Arbeit ist erledigt ;)
        #############################

        # Sessiondaten in die Datenbank schreiben
        self.session.update_session()
        # Datenbank verbindung beenden
        self.db.close()

        # SeitenInhalt in Template einfügen
        try:
            page = template.replace( "<lucidTag:page_body/>", main_content )
        except Exception, e:
            page = "Page Content Error: '%s'<hr>content:<br />%s" % (e, main_content)

        if self.page_msg.data != "":
            # Nachricht vorhanden -> wird eingeblendet
            page_msg = '<div id="page_msg">%s</div>' % self.page_msg.data
        else:
            page_msg = ""
        page = page.replace( "<lucidTag:page_msg/>", page_msg )

        return page.replace( "<lucidTag:script_duration/>", "%.2f" % (time.time() - start_time) )

    def error( self, txt1, *txt2 ):
        txt2 = [str(i) for i in txt2]
        txt2 = "<br/>".join( txt2 )
        print "Content-type: text/html\n"
        print "<h1>Internal Error!</h1>"
        print "<h2>%s</h2>" % txt1
        print "<h3>%s</h3>" % txt2
        sys.exit()

    #_____________________________________________________________________________________________________

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

    #_____________________________________________________________________________________________________

    def detect_page( self ):
        "Findet raus welches die aktuell anzuzeigende Seite ist"

        if self.CGIdata.has_key( "page_id" ):
            # Bei Modulen kann die ID schon in der URL mitgeschickt werden.
            self.check_page_id( self.CGIdata["page_id"] )
            return

        if self.CGIdata.has_key( "command" ):
            # Ein internes Kommando (LogIn, EditPage ect.) wurde ausgeführt
            self.set_history_page()
            return

        if self.config.system.poormans_modrewrite == True:
            # Auswerten von os.environ-Eintrag "REQUEST_URI"
            try:
                request_uri = os.environ["REQUEST_URI"]
            except KeyError:
                self.error(
                    "Can't use 'poormans_modrewrite':",
                    'There is no REQUEST_URI in Environment!'
                )

            request_uri = request_uri[len(self.config.system.poormans_url):]
            self.check_page_name( request_uri )
            #~ self.debug()
            return

        if len( self.CGIdata ) == 0:
            # keine CGI-Daten vorhanden
            # `-> Keine Seite wurde angegeben -> default-Seite wird angezeigt
            self.set_default_page()
            return

        page_ident = self.config.system.page_ident.replace("?","")
        page_ident = page_ident.replace("=","")
        if self.CGIdata.has_key( page_ident ):
            self.check_page_name( self.CGIdata[page_ident] )
            return

        # Es konnte keine Seite in URL-Parametern gefunden werden, also
        # wird die Standart-Seite genommen
        self.page_name_error = True
        self.set_default_page()

    def check_page_id( self, page_id ):
        """ Testet ob die page_id auch richtig ist """
        db_page_id = self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["id"]
        if db_page_id != page_id:
            self.page_msg( "Page with id '%s' unknow." % page_id )
            self.set_default_page()

    def check_page_name( self, page_name ):
        """ ermittelt anhand des page_name die page_id """
        page_name = urllib.unquote( page_name )

        if page_name == "/":
            # Index Seite wurde aufgerufen. Zumindest bei poor-modrewrite
            self.set_default_page()
            return

        page_name_split = page_name.split("/")[1:]
        page_id = 0
        for name in page_name_split:
            try:
                page_id = self.db.select(
                        select_items    = ["id"],
                        from_table      = "pages",
                        where           = [ ("name",name), ("parent",page_id) ]
                    )[0]["id"]
            except IndexError,e:
                self.page_msg( "404 - File not found: Page '%s' unknow." % name )
                break

        if page_id == 0:
            #~ self.page_msg( "Page '%s' unknown." % page_name )
            self.set_default_page()
            return

        self.CGIdata["page_id"] = page_id

    def set_history_page( self ):
        if self.session.has_key("page_history"):
            self.CGIdata["page_id"] = self.session["page_history"][0]
        else:
            self.page_msg( "Debug: History nicht vorhanden!" )
            self.set_default_page()

    def set_default_page( self ):
        "Setzt die default-Page als aktuelle Seite"
        self.CGIdata["page_id"] = self.preferences["core"]["defaultPageName"]


    #_____________________________________________________________________________________________________


    def command( self, order ):
        """ Behandelt alle URL-"command="-Parameter """
        #~ print "Content-type: text/html\n"
        #~ print "<pre>"
        #~ for k,v in self.CGIdata.iteritems(): print "%s - %s" % (k,v)
        #~ print "</pre>"
        #~ sys.exit()

        self.log( "Special PyLuid command: '%s'" % order )

        #~ print "Content-type: text/html\n"
        #~ print "<pre>"
        #~ help(module_manager)
        #~ print "</pre>"
        #~ sys.exit()

        # "Kommando"-Daten aus dem Module-Manager holen
        order_data = self.module_manager.get_orders()

        if order in order_data:
            # Der aktuelle URL-command existiert und wird ausgeführt
            return self.module_manager.start_module( order_data[order] )
        else:
            return "<h1>ERROR!</h1><br/>Command unknow!"



if __name__ == "__main__":
    #~ print "Content-type: text/html\n"
    MyLR = LucidRender()
    page_content = MyLR.make()
    print "Content-type: text/html\n"
    print page_content
