#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License http://www.opensource.org/licenses/gpl-license.php"
__url__     = "http://www.PyLucid.org"

__info__ = """<a href="%s" title="PyLucid - A OpenSource CMS in pure Python CGI by Jens Diemer">PyLucid</a> v0.6.0RC2""" % __url__

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

__version__="0.4.1"

__history__="""
v0.4.1
    - Bug: In class path wurde poormans_url nicht gesetzt wenn poormans_modrewrite eingeschaltet war
v0.4
    - NEU: "class path" eigene Klasse um Pfade anzupassen, die auch von install_PyLucid verwendet wird.
    - NEU: check_CSS_request(): damit das CSS direkt zum Browser geschickt werden kann.
v0.3.3
    - page_parser.render() aus dem Module-Manager zur verfügung gestellt
v0.3.2
    - Experimentall: CPU Zeit (time.clock()) wird zusätzlich angezeigt
v0.3.1
    - Backports: Es wird nur der Pfad geändert, wenn Python älter als v2.4 ist. Damit werden erst die
        Backports gefunden und importiert ;)
v0.3.0
    - Großer umbau: Anpassung an neuen Modul-Manager und page_parser.py
v0.2.15
    - Die Umstellung mit check_user_agent() ist doch nicht so einfach gewesen und brauchte
        einige andere Änderungen :(
v0.2.14
    - NEU: check_user_agent() - Für Unterscheidung zwischen Brower und Suchmaschine
v0.2.13
    - Die gefakte 404-Fehlerseite benutzt nun statt HTTP_SERVER die Angaben aus HTTP_HOST. Dies ist besonders
        dann wichtig, wenn auf dem Server nicht die Hauptdomain verwendet wurde.
v0.2.12
    - NEU: verify_page(): Überprüft die Rechte, ob der aktuelle Benutzer die Seite sehen darf, oder nicht
v0.2.11
    - Bug: Die Tabelle session_data hatte einen hardcoded prefix gehabt :( Somit funktionierte
        das ganze System nicht, wenn man als Tabellen-Pefix was anderes außer "lucid_" wählte :(
    - Bug: Fälschlicherweise wurde der page_ident zweimal abgeschnitten, wenn poormans_modrewrite
        nicht benutzt wurde.
v0.2.10
    - Umstellung: __version__ hier in der index.py ist nicht mehr die Versionsnummer von
        PyLucid allgemein! Dafür ist nun der String __info__ alleine zuständig
        *Diese History ist ab jetzt auch nur noch für die index.py zuständig.
        *Die globare History wird auf der Webseite gepflegt.
    - Bug: In check_page_name() wurde config.system.page_ident nicht beachtet
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

#~ print "Content-type: text/html; charset=utf-8\r\n\r\nDEBUG:<pre>"


# Als erstes Mal die Zeit stoppen ;)
import time
start_time = time.time()
start_clock = time.clock()



import cgitb;cgitb.enable()


# Python-Basis Module einbinden
import os, sys, urllib, cgi

from PyLucid_python_backports.utils import *


# Interne PyLucid-Module einbinden
import config # PyLucid Konfiguration
from PyLucid_system import SQL
from PyLucid_system import sessiondata
from PyLucid_system import sessionhandling
from PyLucid_system import SQL_logging
#~ from PyLucid_system import userhandling
from PyLucid_system import module_manager
from PyLucid_system import tools
from PyLucid_system import preferences
from PyLucid_system import page_parser

# Versions-Information übertragen
preferences.__info__    = __info__




class path:
    """
    Passt die verwendeten Pfade an.
    Ist ausgelagert, weil hier und auch gleichzeitig von install_PyLucid verwendet wird.
    """
    def __init__(self, PyLucid):
        self.PyLucid = PyLucid
        self.config = PyLucid["config"]

    def setup(self):
        self.config.system.script_filename = os.path.split(self.config.system.script_filename)[0]

        self.config.system.script_filename = os.path.normpath(self.config.system.script_filename)
        self.config.system.document_root   = os.path.normpath(self.config.system.document_root)

        # Pfad für Links festlegen
        self.config.system.real_self_url = self.config.system.script_filename[len(self.config.system.document_root):]
        self.config.system.real_self_url += "/index.py"

        self.config.system.poormans_url = self.config.system.real_self_url

    def setup_URLs(self):
        URLs    = self.PyLucid["URLs"]
        CGIdata = self.PyLucid["CGIdata"]

        URLs["link"] = "%s%s" % (
            self.config.system.poormans_url, self.config.system.page_ident
        )
        URLs["base"] = "%s?page_id=%s" % (
            self.config.system.real_self_url, CGIdata["page_id"]
        )
        URLs["real_self_url"] = self.config.system.real_self_url
        URLs["poormans_url"] = self.config.system.poormans_url



class cgitb_addon:
    """
    Damit bei einem Trackback-Fehler mit cgitb die page_msg Ausgaben
    erscheinen, wird die reset()-Funktion in cgitb überschrieben.
    """
    def __init__(self, PyLucid):
        self.PyLucid    = PyLucid
        self.page_msg   = PyLucid["page_msg"]
        self.default_reset_code = cgitb.reset()

    def __call__(self):
        sys.stdout = sys.__stdout__ # Evtl. redirectered stdout wiederherstellen
        print "Content-type: text/html; charset=utf-8\r\n"
        print '<h1 style="background-color:#6622aa;color:#ffffff;padding:0.75em;">An Script Error occurred</h1>'

        print "sys.exc_info:", sys.exc_info()

        try:
            self.PyLucid_information()
        except Exception, e:
            self.page_msg("Error:", e)

        print self.page_msg.get()
        return self.default_reset_code

    def PyLucid_information(self):
        """
        Einige interne Informationen einfügen
        """
        print "<h3>PyLucid-Object dict-keys:</h3>"
        print self.PyLucid.keys()

        try:
            print "<h3>Error handling:</h3>"
            print "<pre>"
            print "ModuleManager_error_handling..:", self.PyLucid["config"].system.ModuleManager_error_handling
            print "ModuleManager_import_error....:", self.PyLucid["config"].system.ModuleManager_import_error
            print "</pre>"
        except Exception, e:
            print "</pre>not available:", e

        try:
            self.PyLucid["CGIdata"].debug() # Debug-Ausgaben in page_msg
        except KeyError:
            pass

        try:
            print "<h3>session data:</h3>"
            data = self.PyLucid["session"].iteritems()
            print "<pre>"
            for k,v in data:
                print "%20s:%s" % (k,v)
            print "</pre>"
        except Exception, e:
            print "not available:", e

        try:
            print "<h3>Last 3 logs:</h3>"
            data = self.PyLucid["db"].get_last_logs(3)
            print self.PyLucid["tools"].make_table_from_sql_select(
                data,
                id          = "internals_log_data",
                css_class   = "internals_table"
            )
        except Exception, e:
            print "not available:", e

        try:
            print "<h3>self.URLs:</h3>"

            values = [(len(v),k,v) for k,v in self.PyLucid["URLs"].iteritems()]
            values.sort()

            print "<pre>"
            for _,k,v in values:
                print "%15s:%s" % (k,v)
            print "</pre>"
        except Exception, e:
            print "not available:", e



save_max_history_entries = 10

class LucidRender:
    def __init__( self ):
        # Alle Objekte/Klassen, die für Module/Plugins nötig sein könnten, werden
        # in dem Dict PyLucid_objects abgelegt. Dieses erlaubt ein vereinheitliche
        # Instanzierung von Modulen
        self.PyLucid = {
            "URLs": {},
        }

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.page_msg       = sessiondata.page_msg()
        self.PyLucid["page_msg"] = self.page_msg

        # Überschreiben der reset() Funktion in cgitb, damit die page_msg angezeigt
        # werden.
        cgitb.reset = cgitb_addon(self.PyLucid)

        # PyLucid's Konfiguration
        self.config         = config
        self.PyLucid["config"] = self.config

        self.path = path(self.PyLucid)

        # Anhand des user agent werden die Pfade und evtl. gesetzt
        self.check_user_agent()

        #~ self.page_msg( "Debug, poormans_modrewrite:", config.system.poormans_modrewrite )
        #~ self.page_msg( "Debug, script_filename.: '%s'" % config.system.script_filename )
        #~ self.page_msg( "Debug, document_root...: '%s'" % config.system.document_root )
        #~ self.page_msg( "Debug, real_self_url...: '%s'" % config.system.real_self_url )
        #~ self.page_msg( "Debug, poormans_url....: '%s'" % config.system.poormans_url )

        if self.config.system.poormans_modrewrite == True:
            # Frühzeite überprüfung der URL
            self.check_request()

        # CGI Post/Get Daten
        self.CGIdata        = sessiondata.CGIdata( self.PyLucid )
        #~ self.CGIdata.debug()
        self.PyLucid["CGIdata"] = self.CGIdata

        tools.PyLucid           = self.PyLucid
        self.PyLucid["tools"]   = tools

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.db            = SQL.db(self.PyLucid)
        self.PyLucid["db"] = self.db

        self.check_CSS_request()

        # Verwaltung für Einstellungen aus der Datenbank
        self.preferences            = preferences.preferences( self.PyLucid )
        self.PyLucid["preferences"] = self.preferences

        # Log-Ausgaben in SQL-DB
        self.log            = SQL_logging.log( self.PyLucid )
        self.PyLucid["log"] = self.log

        # Allgemeiner CGI Sessionhandler auf mySQL-Basis
        self.session        = sessionhandling.sessionhandler( self.PyLucid, page_msg_debug=False )
        #~ self.session        = sessionhandling.sessionhandler( self.PyLucid, page_msg_debug=True )
        #~ self.session.debug()
        self.PyLucid["session"] = self.session

        # Für die Log-Einträge Informationen festhalten
        self.log.client_sID         = self.session.ID
        if self.session.has_key("user"):
            self.log.client_user_name   = self.session["user"]

        # Aktuelle Seite ermitteln und festlegen
        self.detect_page()
        # Überprüfe Rechte der Seite
        self.verify_page()

        # URLs zusammenbauen, die immer gleich sind.
        self.path.setup_URLs()

        self.parser = page_parser.parser( self.PyLucid )
        self.PyLucid["parser"] = self.parser

        self.render = page_parser.render( self.PyLucid )
        self.PyLucid["render"] = self.render

        # Verwaltung von erweiterungs Modulen/Plugins
        self.module_manager = module_manager.module_manager( self.PyLucid )
        #~ self.module_manager.debug()
        self.PyLucid["module_manager"] = self.module_manager

        # Der ModulManager, wird erst nach dem Parser instanziert. Damit aber der Parser
        # auf ihn zugreifen kann, packen wir ihn einfach dorthin ;)
        self.parser.module_manager = self.module_manager

    def check_CSS_request(self):
        """
        Beantwortet direkt eine CSS anfrage wie:
        /index.py?page_id=1&amp;command=page_style&amp;action=print_current_style
        """
        def check(key, value):
            if self.CGIdata.has_key(key) and self.CGIdata[key] == value:
                return True
            return False

        if not ( check("command","page_style") and check("action","print_current_style") ):
            return

        print "Content-type: text/css; charset=utf-8\r\n"
        sys.stdout.write(self.db.side_style_by_id(self.CGIdata["page_id"]))
        sys.exit()

    def setup_parser(self):
        """
        Den page_parser Einrichten
        """
        page_parser.__info__    = __info__
        page_parser.start_time  = start_time

        # "Statische" Tag's definieren
        self.parser.tag_data["powered_by"]  = __info__
        if self.session["user"] != False:
            self.parser.tag_data["script_login"] = \
            '<a href="%s?page_id=%s&amp;command=auth&amp;action=logout">logout [%s]</a>' % (
                self.config.system.real_self_url, self.CGIdata["page_id"], self.session["user"]
            )
        else:
            self.parser.tag_data["script_login"] = \
            '<a href="%s?page_id=%s&amp;command=auth&amp;action=login">login</a>' % (
                self.config.system.real_self_url, self.CGIdata["page_id"]
            )

    #_____________________________________________________________________________________________________

    def check_user_agent( self ):
        """
        Legt Pfade und poormans_modrewrite fest.

        Anhand des user-agent wird poormans_modrewrite evtl. ausgeschaltet, damit Suchmaschinen
        die Seiten auch indexieren, dürfen sie keine poormans_modrewrite 404 Fehlerseiten "sehen".
        """
        # Pfade setzten, ist ausgelagert, weil es auch von install_PyLucid genutzt wird
        #~ path(config).setup()
        self.path.setup()

        if config.system.poormans_modrewrite == False:
            # poormans_modrewrite wird eh nicht verwendet
            return

        try:
            user_agent = os.environ["HTTP_USER_AGENT"]
        except KeyError:
            # Der Client schickt nicht den user agent, also gibt's kein poormans_modrewrite
            pass
        else:
            for word in config.system.mod_rewrite_user_agents:
                if user_agent.find( word ) != -1:
                    # poormans_modrewrite: activated
                    config.system.page_ident = ""
                    #~ self.page_msg( "Debug: Browser identified, poormans_modrewrite activated." )

                    if config.system.real_self_url == "/index.py":
                        # Ist im Hauptverzeichnis installiert
                        config.system.poormans_url = ""
                    else:
                        # Dateiname (index.py) abscheiden
                        config.system.poormans_url = os.path.split( config.system.real_self_url )[0]

                    return

        # Es wurde kein Browser erkannt, also wird kein poormans_modrewrite
        # verwendet.
        #~ self.page_msg( "Debug: Browser not identified, poormans_modrewrite deactivated." )
        config.system.poormans_modrewrite = False

        # Damit die Links absolut sind:
        config.system.poormans_url = config.system.real_self_url

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

        if clean_url == config.system.real_self_url:
            # PyLucid's index.py wird aufgerufen
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
            deep_url.insert(0, os.environ["HTTP_HOST"] )
            # URL zusammensetzten
            deep_url = "http://%s" % "/".join( deep_url )
        except KeyError:
            # URL zusammensetzten
            deep_url = "/%s" % "/".join( deep_url )

        alternative_urls.append( deep_url )


        try:
            root_url = "http://%s%s" % (os.environ["HTTP_HOST"], self.config.system.real_self_url )
        except KeyError:
            root_url = self.config.system.real_self_url

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

        print "<address>%s</adress>" % __info__
        print "</body></html>"

        sys.exit()

    #_____________________________________________________________________________________________________

    def make( self ):
        "Baut die Seite zusammen und liefert sie zurück"

        if self.CGIdata.has_key("command"):
            # Ein Kommando soll ausgeführt werden
            module_content = self.module_manager.run_command()
            #~ self.page_msg( "X%sX" % module_content )
        else:
            module_content = None

        # Information der Seite aus DB holen
        # Wird erst gemacht, nachdem ein Kommando ausgeführt wird, weil evtl.
        # das Kommando die aktuelle Seite geändert hat (z.B. edit_page)
        try:
            side_data = self.db.get_side_data( self.CGIdata["page_id"] )
        except IndexError, e:
            self.page_msg( "Can get Page: %s" % e, "page_id: %s" % self.CGIdata["page_id"] )
            self.set_default_page()
            try:
                side_data = self.db.get_side_data( self.CGIdata["page_id"] )
            except IndexError, e:
                self.error( "Can get Page: %s" % e, "page_id: %s" % self.CGIdata["page_id"] )

        if (module_content != None) and (module_content != ""):
            # Das Modul selber hat eine Seite erzeugt, die Angezeigt werden soll
            if type( module_content ) == tuple:
                side_data["content"]    = module_content[0]
                side_data["markup"]     = module_content[1]
            else:
                # Einfacher rückgabe der Daten -> Markup ist immer none
                side_data["content"]    = module_content
                side_data["markup"]     = "none"

        self.setup_parser()

        #~ self.page_msg( "Debug, markup:", side_data["markup"] )

        # Alle Tags ausfüllen und Markup anwenden
        side_content = self.render.render( side_data )


        # Alle Tags im Template ausfüllen und dabei die Seite in Template einbauen
        page = self.render.apply_template( side_content, side_data["template"] )

        if self.session.ID != False:
            # Es wurde eine Session eröffnet/geladen, die nun wieder gespeichert wird
            self.save_page_history()

            # Sessiondaten in die Datenbank schreiben
            self.session.update_session()

        # Datenbank verbindung beenden
        self.db.close()

        #~ # Debug für die Pfade
        #~ for k,v in self.PyLucid["URLs"].iteritems():
            #~ self.page_msg("%15s: %s" % (k,v))

        ## gesammelte Seiten-Nachrichten einblenden
        # s. sessiondata.page_msg()
        page = page.replace( "<lucidTag:page_msg/>", self.page_msg.get() )

        end_time = time.time()
        end_clock = time.clock()
        time_string = "%.2fCPU %.2f" % (end_clock-start_clock, end_time-start_time)
        #~ return page.replace( "<lucidTag:script_duration/>", "%.2f" % (time.time() - start_time) )
        return page.replace( "<lucidTag:script_duration/>", "%s" % time_string )

    #_____________________________________________________________________________________________________

    def error( self, txt1, *txt2 ):
        """ Allgemeine Fehler-Ausgabe """
        print "Content-type: text/html; charset=utf-8\r\n\r\n"
        print "<h1>Internal Error!</h1>"
        print "<h2>%s</h2>" % txt1
        print "<h3>%s</h3>" % "<br/>".join( [str(i) for i in txt2] )
        print "<hr><address>%s</address>" % __info__
        sys.exit()

    #_____________________________________________________________________________________________________

    def save_page_history( self ):
        """
        Speichert in session["page_history"] die ID's der besuchten Seiten
        """
        if not self.session.has_key("page_history"):
            # Noch keinen History vorhanden (User gerad erst eingeloggt)
            self.session["page_history"] = [ self.CGIdata["page_id"] ]
            return

        if self.session["page_history"][0] == self.CGIdata["page_id"]:
            # Ist noch die selbe Seite -> wird nicht abgespeichert
            return
        else:
            # History kürzen
            self.session["page_history"] = self.session["page_history"][:save_max_history_entries]

            # Fügt die aktuelle Seite am Anfang der Liste ein
            self.session["page_history"].insert( 0, self.CGIdata["page_id"] )


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

            # Scheidet das evtl. vorhandene Verzeichnis ab, in dem sich PyLucid
            # befindet. Denn das gehört nicht zum Seitennamen den der User sehen will.
            if request_uri.startswith( self.config.system.poormans_url ):
                request_uri = request_uri[len(self.config.system.poormans_url):]

            #~ self.page_msg( "request_uri:", request_uri )

            self.check_page_name( request_uri )
            return

        if len( self.CGIdata ) == 0:
            # keine CGI-Daten vorhanden
            # `-> Keine Seite wurde angegeben -> default-Seite wird angezeigt
            self.set_default_page()
            return

        page_ident = self.config.system.page_ident.replace("?","")
        page_ident = page_ident.replace("=","")
        if self.CGIdata.has_key( page_ident ):
            #~ self.CGIdata.debug()
            #~ self.page_msg( cgi.escape( self.CGIdata[page_ident] ) )
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
        try:
            db_page_id = self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["id"]
        except IndexError:
            pass
        else:
            if db_page_id == page_id:
                # Alles OK
                return

        self.page_msg( "404 Not Found. Page with id '%s' unknown." % page_id )
        self.set_default_page()

    def check_page_name( self, page_name ):
        """ ermittelt anhand des page_name die page_id """

        # Aufteilen: /bsp/ -> ['','%3ClucidTag%3ABsp%2F%3E','']
        page_name_split = page_name.split("/")

        # unquote + Leere Einträge löschen: ['','%3ClucidTag%3ABsp%2F%3E',''] -> ['<lucidTag:Bsp/>']
        page_name_split = [urllib.unquote_plus(i) for i in page_name_split if i!=""]

        #~ page_name = urllib.unquote(  )
        #~ self.CGIdata["REQUEST_URI"] = urllib.unquote_plus(page_name)

        if page_name == "/" or page_name == "":
            # Index Seite wurde aufgerufen. Zumindest bei poor-modrewrite
            self.set_default_page()
            return

        page_id = 0
        for name in page_name_split:
            #~ self.page_msg( name )
            if name.startswith("index.py?") and name[-1] == "=":
                # Ist ein Parameter und kein Seitenname
                continue

            try:
                page_id = self.db.select(
                        select_items    = ["id","parent"],
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
        try:
            self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ["id",self.CGIdata["page_id"]]
            )[0]["id"]
        except IndexError:
            # Die defaultPageName Angabe ist falsch
            self.page_msg("default Page with ID %s not found!" % self.CGIdata["page_id"] )
            try:
                self.CGIdata["page_id"] = self.db.select(
                    select_items    = ["id"],
                    from_table      = "pages",
                    order           = ("id","ASC"),
                    limit           = (0,1) # Nur den ersten ;)
                )[0]["id"]
            except IndexError:
                # Es gibt wohl überhaupt keine Seite???
                self.error("Can't find pages!", self.page_msg.data)

    def verify_page( self ):
        """
        Überprüft die Rechte, ob der aktuelle Benutzer die Seite sehen darf, oder nicht
        """
        #~ self.CGIdata.debug()

        page_id = self.CGIdata["page_id"]
        try:
            page_permitViewPublic = self.db.get_permitViewPublic( page_id )
        except IndexError:
            self.page_msg( "Can't find page." )
            self.set_default_page()
            return
        #~ self.page_msg( "page_permitViewPublic:",page_permitViewPublic )

        if self.session.has_key("isadmin") and self.session["isadmin"] == True:
            # Administratoren dürfen immer alle Seiten sehen
            return
        else:
            # User ist nicht eingeloggt
            if page_permitViewPublic != 1:
                self.page_msg("401 Unauthorized. You must login to see this page!")
            else:
                # Seite ist öffentlich
                return

        # Die Aktuelle Seite darf nicht angezeigt werden -> Zeige die default Seite
        self.set_default_page()






if __name__ == "__main__":
    #~ print "Content-type: text/html; charset=utf-8\r\n" # Debugging
    #~ tools.stdout_marker() # Debug: Alle print-Ausgaben makieren
    #~ print "<pre>"
    page_content = LucidRender().make()
    #~ print "</pre>"

    print "Content-type: text/html; charset=utf-8\r\n"
    print page_content
