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

__version__="0.2.9"

__history__="""
v0.2.9
    - NEU: check_request() - Frühzeitige Abhandlung von 404 Fehlern
    - check_page_name() angepasst
    - save_page_history() überarbeitet
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


#~ print "Content-type: text/html; charset=utf-8\r\n\r\nDEBUG:"
#~ sys.exit()

#~ print sys.version
if not sys.version.startswith("2.4"):
    # Für alle Versionen von Python vor 2.4 werden die Backports importiert
    from PyLucid_python_backports.utils import *


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

        # PyLucid's Konfiguration
        self.config         = config
        self.PyLucid["config"] = self.config

        if self.config.system.poormans_modrewrite == True:
            # Frühzeite überprüfung der URL
            self.check_request()

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.page_msg       = sessiondata.page_msg()
        self.PyLucid["page_msg"] = self.page_msg

        # CGI Post/Get Daten
        self.CGIdata        = sessiondata.CGIdata( self.PyLucid )
        #~ self.CGIdata.debug()
        self.PyLucid["CGIdata"] = self.CGIdata

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.db             = SQL.db()
        self.PyLucid["db"] = self.db

        # Verwaltung für Einstellungen aus der Datenbank
        self.preferences    = preferences.preferences( self.PyLucid )
        self.PyLucid["preferences"] = self.preferences

        tools.PyLucid = self.PyLucid
        self.PyLucid["tools"] = tools

        # Log-Ausgaben in SQL-DB
        self.log            = SQL_logging.log( self.PyLucid )
        self.PyLucid["log"] = self.log

        # Allgemeiner CGI Sessionhandler auf mySQL-Basis
        self.session        = sessionhandling.sessionhandler(
            self.db.cursor, "lucid_session_data", self.log,
            CookieName="PyLucid_id"
        )
        self.session.page_msg = self.page_msg
        #~ self.session.debug()
        self.PyLucid["session"] = self.session

        # Für die Log-Einträge Informationen festhalten
        self.log.client_sID         = self.session.ID
        if self.session.has_key("user"):
            self.log.client_user_name   = self.session["user"]

        # Aktuelle Seite ermitteln und festlegen
        self.detect_page()

        # Verwaltung von erweiterungs Modulen/Plugins
        self.module_manager = module_manager.module_manager( self.PyLucid )
        # Alle Module, die für den Modul-Manager vorbereitet wurden einlesen
        self.module_manager.read_module_info( "PyLucid_modules" )
        #~ self.module_manager.debug()
        self.PyLucid["module_manager"] = self.module_manager

        # Zum Zusammenbau der HTML-Seiten
        self.pagerender     = pagerender.pagerender( self.PyLucid )

    #_____________________________________________________________________________________________________

    def check_request( self ):
        """
        Überprüft die Anfrage, wenn mit poormans_modrewrite gearbeitet wird.

        Wird mit Apache's "ErrorDocument 404" auf PyLucid's index.py verwiesen, solle dennoch
        angezeigt werden, wenn eine echte falsche URL abgerufen wurde. z.B. die Anforderung
        eines nicht existierenden Bildes! In dem Falle sollte nicht die Komplette Startseite des
        CMS aufgebaut werden, sondern einfach nur eine kleine Fehler-Seite ;)
        """
        try:
            request_uri = os.environ["REQUEST_URI"]
        except KeyError:
            self.error(
                "Can't use 'poormans_modrewrite':",
                'There is no REQUEST_URI in Environment!'
            )

        # URL Parameter abschneiden
        try:
            clean_url = request_uri[:request_uri.index("?")]
        except ValueError:
            # Kein URL Parameter vorhanden
            clean_url = request_uri

        if clean_url == self.config.system.real_self_url:
            # Direkter Aufruf von PyLucid's index.py, also alles OK
            return

        # URL Parameter abschneiden

        try:
            file_ext = clean_url[clean_url.rindex(".")+1:]
        except ValueError:
            # Ist keine Datei, die angefordert wird, könnte alles OK sein
            return

        if len(file_ext) > 4:
            # Der gefunde Punkt ist wohl kein Trennzeichen für ein Dateiende
            return

        if not file_ext in self.config.system.mod_rewrite_filter:
            # Dateiendung ist nicht im Filter erhalten
            return

        ##
        ## Die URL ist also nicht korrekt
        ##

        print "Content-Type: text/html\r\n"
        print "<html><head><title>404 Not Found</title></head><body>"
        print "<h1>Not Found</h1>"
        print "<p>The requested URL %s was not found on this server.</p>" % clean_url

        alternative_urls = []
        # Aufteilen, Leere Einträge löschen sowie letzten Eintrag abschneiden:
        # /bsp/bild.gif -> ['','bsp','bild.gif'] -> ['bsp','bild.gif'] -> ['bsp']
        deep_url = [i for i in request_uri.split("/") if i!=""][:-1]
        try:
            # Server Adresse einfügen
            deep_url.insert(0, os.environ["SERVER_NAME"] )
            # URL zusammensetzten
            deep_url = "http://%s" % "/".join( deep_url )
        except KeyError:
            # URL zusammensetzten
            deep_url = "/%s" % "/".join( deep_url )

        alternative_urls.append( deep_url )


        try:
            root_url = "http://%s%s" % (os.environ["SERVER_NAME"], self.config.system.poormans_url )
        except KeyError:
            root_url = self.config.system.poormans_url

        alternative_urls.append( root_url )

        # Doppelte Einträge per set() löschen
        alternative_urls = set( alternative_urls )

        # URLs zusammen bauen
        urllist = ['<a href="%s">%s</a>' % (u,u) for u in alternative_urls]

        # Alternative URLs Anzeigen
        print "<p>try:</br>"
        print "<br/>or</br>".join( urllist )
        print "</p>"

        #~ print "<pre>"
        #~ print request_uri
        #~ print clean_url
        #~ print file_ext, len( file_ext )
        #~ print "</pre>"
        #~ import cgi ; cgi.print_environ()

        print "<hr>"

        try:
            print os.environ["SERVER_SIGNATURE"]
        except KeyError:
            pass

        print "</body></html>"

        sys.exit()

    #_____________________________________________________________________________________________________

    def make( self ):
        "Baut die Seite zusammen und liefert sie zurück"

        if self.CGIdata.has_key("command"):
            # Ein Kommando soll ausgeführt werden
            module_content = self.command( self.CGIdata["command"] )
        else:
            module_content = None

        # Information der Seite aus DB holen
        try:
            side_data = self.db.get_side_data( self.CGIdata["page_id"] )
        except IndexError, e:
            self.error( "Can get Page: %s" % e, "page_id: %s" % self.CGIdata["page_id"] )

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

        if self.session.ID != False:
            # User ist eingeloggt -> Es werden Informationen gespeichert.
            self.save_page_history()

        #~ self.page_msg( "Markup:",side_data["markup"] )
        return self.build_side( side_data )


    def build_side( self, side_data ):

        # Parsen des SeitenInhalt, der Aufgerufenen Seite
        main_content = self.pagerender.lucidTag_page_body( side_data )

        #~ self.page_msg( main_content )

        if type(main_content) != str:
            # Mit dem Inhalt stimmt was nicht!
            main_content = "<h1>Internal contenttyp error (not String)!</h1><br/>Content:<hr/>" + str( main_content )

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

        ## gesammelte Seiten-Nachrichten einblenden
        # s. sessiondata.page_msg()
        if self.page_msg.data != "":
            # Nachricht vorhanden -> wird eingeblendet
            page_msg = '<div id="page_msg">%s</div>' % self.page_msg.data
        else:
            page_msg = ""
        page = page.replace( "<lucidTag:page_msg/>", page_msg )

        return page.replace( "<lucidTag:script_duration/>", "%.2f" % (time.time() - start_time) )

    #_____________________________________________________________________________________________________

    def error( self, txt1, *txt2 ):
        """ Allgemeine Fehler-Ausgabe """
        print "Content-type: text/html; charset=utf-8\r\n\r\n"
        print "<h1>Internal Error!</h1>"
        print "<h2>%s</h2>" % txt1
        print "<h3>%s</h3>" % "<br/>".join( [str(i) for i in txt2] )
        sys.exit()

    #_____________________________________________________________________________________________________

    def save_page_history( self ):
        """
        Speichert in session["page_history"] die ID's der besuchten Seiten
        """
        try:
            # History kürzen
            self.session["page_history"] = self.session["page_history"][:save_max_history_entries]

            # Fügt die aktuelle Seite am Anfang der Liste ein
            self.session["page_history"].insert( 0, self.CGIdata["page_id"] )
        except KeyError:
            # Noch keinen History vorhanden (User gerad erst eingeloggt)
            self.session["page_history"] = [ self.CGIdata["page_id"] ]


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
        self.set_default_page()

    def set_history_page( self ):
        if self.session.has_key("page_history"):
            self.CGIdata["page_id"] = self.session["page_history"][0]
        else:
            self.page_msg( "Debug: History nicht vorhanden!" )
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

        #~ # URL Parameter abschneiden
        #~ try:
            #~ clean_page_name = page_name[:page_name.index("?")]
        #~ except ValueError:
            #~ # Kein URL Parameter vorhanden
            #~ clean_page_name = page_name

        # Aufteilen: /bsp/ -> ['','bsp','']
        page_name_split = page_name.split("/")

        # Leere Einträge löschen: ['','bsp',''] -> ['bsp']
        page_name_split = [i for i in page_name_split if i!=""]

        page_id = 0
        for name in page_name_split:
            try:
                page_id = self.db.select(
                        select_items    = ["id"],
                        from_table      = "pages",
                        where           = [ ("name",name), ("parent",page_id) ]
                    )[0]["id"]
            except Exception,e:
                if self.config.system.real_self_url == os.environ["REQUEST_URI"]:
                    # Aufruf der eigenen index.py Datei
                    self.set_default_page()
                    return
                else:
                    self.page_msg( "404 Not Found. The requested URL '%s' was not found on this server." % name )
                    #~ self.page_msg( page_name_split )
                    if page_id == 0:
                        # Nur wenn nicht ein Teil der URL stimmt, wird auf die Hauptseite gesprunngen
                        self.set_default_page()
                        return

        self.CGIdata["page_id"] = int( page_id )

    def set_default_page( self ):
        "Setzt die default-Page als aktuelle Seite"
        try:
            self.CGIdata["page_id"] = self.preferences["core"]["defaultPageName"]
        except KeyError:
            self.error(
                "Can'r read preferences from DB.",
                "(Did you install PyLucid correctly?)"
            )


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
    print "Content-type: text/html; charset=utf-8\r\n\r\n"
    print page_content
