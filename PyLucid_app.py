#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = """GNU General Public License v2 or above -
 http://www.opensource.org/licenses/gpl-license.php"""
__url__     = "http://www.PyLucid.org"

__version__ = "0.7.1beta"
__info__ = """<a href="%s" title="\
PyLucid - A OpenSource CMS in pure Python CGI by Jens Diemer">PyLucid</a> \
v%s""" % (__url__, __version__)


#~ debug = True
debug = False



import cgi, os, time
import sys #Debug



#~ class PrintLocator(object):
    #~ """
    #~ Very slow! But in some case very helpfully ;)
    #~ """
    #~ def __init__(self):
        #~ self.oldFileinfo = ""

    #~ def write(self, *txt):
        #~ # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
        #~ stack = inspect.stack()[1]
        #~ fileinfo = (stack[1].split("/")[-1][-40:], stack[2])

        #~ if fileinfo != self.oldFileinfo:
            #~ self.oldFileinfo = fileinfo

            #~ sys.__stdout__.write("\n")
            #~ sys.__stdout__.write("...%s, line %3s:\n" % fileinfo)

        #~ txt = " ".join([str(i) for i in txt])
        #~ sys.__stdout__.write(txt)

#~ import inspect
#~ sys.stdout = PrintLocator()






from PyLucid.system.exceptions import *

# Colubrid
from colubrid import BaseApplication

WSGIrequestKey = "colubrid.request."


#~ import config # PyLucid Grundconfiguration

#__init__
from PyLucid.system import response
from PyLucid.system import tools
from PyLucid.system import URLs
from PyLucid.system import preferences

# init2
from PyLucid.system import sessionhandling
from PyLucid.system import SQL_logging
from PyLucid.system import module_manager
from PyLucid.system import page_parser
from PyLucid.system import detect_page
from PyLucid.system import template_engines


response.__info__ = __info__ # Übertragen







class runlevel(object):
    state = "init"

    def set_install(self):
        self.state = "install"
    def set_command(self):
        self.state = "command"
    def set_normal(self):
        self.state = "normal"

    def is_install(self):
        return self.state == "install"
    def is_command(self):
        return self.state == "command"
    def is_normal(self):
        return self.state == "normal"

    def save(self):
        """Save the current runlevel for a later restore"""
        self.saved_state = self.state
    def restore(self):
        """Set the state to the old prior saved state"""
        self.state = self.saved_state

    def __cmp__(self, _):
        raise RuntimeError, "Old access to runlevel!"

    def __repr__(self):
        return "<runlevel object with state = '%s'>" % self.state












class PyLucidApp(BaseApplication):
    """
    Klasse die die Programmlogik zusammenstellt
    """

    # Angaben für colubrid:
    charset = 'utf-8'
    #~ slash_append = True
    slash_append = False


    def __init__(self, environ, start_response):
        super(PyLucidApp, self).__init__(environ, start_response)

        self.environ = environ

        # Eigenes response-Objekt. Eigentlich genau wie das
        # original von colubrid, nur mit einer kleinen Erweiterung
        self.response = response.HttpResponse()

        # Damit man von überall einen Debug einleiten kann
        self.response.debug = self.request_debug

        self.runlevel = self.request.runlevel = runlevel()

        # Verwaltung für Einstellungen aus der DB (Objekt aus der Middleware)
        self.preferences = self.request.preferences = preferences.Preferences(
            environ['PyLucid.config']
        )

        # 'Speicher' für CSS/JS Daten, die erst am Ende in die CMS Seite
        # eingefügt wird
        self.response.addCode = environ["PyLucid.addCode"]

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.page_msg = self.response.page_msg = environ['PyLucid.page_msg']
        #~ self.page_msg("page_msg - NORMAL")
        #~ self.page_msg.red("page_msg - RED")
        #~ self.page_msg.green("page_msg - GREEN")
        #~ self.page_msg.debug("page_msg - DEBUG")

        # Allgemeiner CGI Sessionhandler auf mySQL-Basis
        self.session = self.request.session = sessionhandling.sessionhandler()

        # Log-Ausgaben in SQL-DB
        self.log = self.request.log = SQL_logging.log()

        # Verwaltung von erweiterungs Modulen/Plugins
        self.module_manager = self.request.module_manager = \
                                                module_manager.module_manager()

        self.render = self.request.render = page_parser.render()

        self.staticTags = self.request.staticTags = response.staticTags()

        # Passt die verwendeten Pfade an.
        self.URLs = self.request.URLs = URLs.URLs(self.request, self.response)

        # Tools an Request Objekt anhängen
        tools.request       = self.request  # Objekt übergeben
        tools.response      = self.response # Objekt übergeben
        self.tools = self.request.tools = tools

        self.response.echo = tools.echo() # Echo Methode an response anhängen

        # Jinja-Context anhängen
        self.request.context = {}

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.db = self.request.db = environ['PyLucid.database']

        # Einheitliche Schnittstelle zu den Templates Engines
        self.request.templates = template_engines.TemplateEngines(
            self.request, self.response
        )

        # FIXME: Übertragen von Objekten in den DBwrapper
        self.db.page_msg    = self.page_msg
        self.db.tools       = self.tools
        self.db.URLs        = self.URLs
        self.db.preferences = self.preferences

    def request_debug(self):
        try:
            import inspect
            # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
            stack = inspect.stack()[1]
            filename = stack[1].split("/")[-1][-20:]
            fileinfo = "%-20s line %3s: " % (filename, stack[2])
            self.page_msg(fileinfo.replace(" ","&nbsp;"))
        except Exception, e:
            self.page_msg("<small>(inspect Error: %s)</small> " % e)
        try:
            from colubrid.debug import debug_info
            self.page_msg(debug_info(self.request))
        except Exception, e:
            self.page_msg("Can't make debug info: %s" % e)

    def setup_runlevel(self):

        pathInfo = self.URLs["pathInfo"]
        #~ self.page_msg(">>>", pathInfo)

        if pathInfo.startswith(self.preferences["installURLprefix"]):
            self.runlevel.set_install()
        elif pathInfo.startswith(self.preferences["commandURLprefix"]):
            self.runlevel.set_command()
        else:
            self.runlevel.set_normal()

        # Pfade anhand des Runlevel anpassen.
        self.URLs.setup_runlevel()

    def init2(self):
        """
        Getrennt vom normalen init, weil zwischenzeitlich evtl. nur ein CSS
        ausgeliefert werden sollte oder PyLucid installieret werden soll...
        Dazu sind die restilichen Objekte garnicht nötig.
        """
        # Preferences aus der DB lesen
        self.preferences.init2(self.request, self.response)
        self.preferences.update_from_sql(self.db)

        # Log-Ausgaben in SQL-DB
        self.log.init2(self.request, self.response)
        #~ self.request.log.debug_last()

        self.session.init2(self.request, self.response)

        self.staticTags.init2(self.request, self.response)

        self.render.init2(self.request, self.response)

        self.module_manager.init2(self.request, self.response)
        #~ self.request.module_manager.debug()

        # Aktuelle Seite ermitteln und festlegen
        try:
            detect_page.detect_page(self.request, self.response).detect_page()
        except NoPageExists:
            # Es existiert noch keine CMS Seite
            self.create_first_page()
        # Überprüfe Rechte der Seite
        #~ self.verify_page()

        # Übertragen von Objekten
        self.db.render = self.render
        self.db.session = self.session

        self.response.module_manager = self.module_manager
        self.response.staticTags = self.staticTags

        # Statische-Tag-Informationen setzten:
        self.staticTags.setup()

    def create_first_page(self):
        from PyLucid.modules.pageadmin import pageadmin
        p = pageadmin.pageadmin(self.request, self.response)
        p.create_first_page()
        msg = (
            '<p>No Page exists.</p>\n'
            '<p>First page created now, please reload :)</p>\n'
        )
        raise NoPageExists(msg)

    def process_request(self):
        try:
            self.db.connect(self.preferences)
        except database.ConnectionError, e:
            raise ConnectionError(e)

        self.environ["request_start"] = time.time()

        self.setup_runlevel()

        if self.runlevel.is_install():
            self.installPyLucid()
            return self.response

        # init der Objekte für einen normalen Request:
        self.init2()

        if self.runlevel.is_normal():
            # Normale CMS Seite ausgeben
            self.normalRequest()

        elif self.runlevel.is_command():
            # Ein Kommando soll ausgeführt werden
            moduleOutput = self.module_manager.run_command()
            if callable(moduleOutput):
                # Wird wohl ein neues response-Objekt sein.
                # z.B. bei einem Dateidownload!
                return moduleOutput

            # Ausgaben vom Modul speichern, dabei werden diese automatisch
            # im response-Objekt gelöscht, denn ein "command"-Modul schreib
            # auch, wie alle anderen Module ins response-Object ;)
            content = self.response.get()

            if "render follow" in self.session:
                # Eintrag löschen, damit der nicht in die DB für den nächsten
                # request gespeichert wird:
                del(self.session["render follow"])

                # Es soll nicht die Ausgaben den Modules angezeigt werden,
                # sondern die normale CMS Seite. (z.B. nach dem Speichern
                # einer editierten Seite!)
                self.normalRequest()
            else:
                # Ausgaben vom Modul sollen in die Seite eingebaut werden:
                self.staticTags["page_body"] = content
                self.render.write_command_template()

        else:
            # Kann eigentlich nie passieren ;)
            raise RuntimeError("unknown runlevel!!!")

        # Evtl. vorhandene Sessiondaten in DB schreiben
        self.session.commit()

        if debug:
            self.response.debug()

        return self.response


    def normalRequest(self):
        # Normale Seite wird ausgegeben

        # Schreib das Template mit dem page_body-Tag ins
        # response Objekt.
        self.render.write_page_template()


    def debug(self, *txt):
        #~ sys.stderr.write(
        self.page_msg(
            "%s\n" % " ".join([str(i) for i in txt])
        )

    def installPyLucid(self):
        """
        Der aktuelle request ist im "_install"-Bereich
        """
        from PyLucid.install.install import InstallApp
        InstallApp.__info__ = __info__
        InstallApp(self.request, self.response).process_request()






app = PyLucidApp

# database
#~ from PyLucid.middlewares.database import DatabaseMiddleware
from PyLucid.middlewares import database
app = database.DatabaseMiddleware(app)

# Configuration
from PyLucid.middlewares.configuration import configMiddleware
app = configMiddleware(app)

# Middleware Page-Message-Object
from PyLucid.middlewares.page_msg import page_msg
app = page_msg(app, debug=False)
#~ app = page_msg(app, debug=True)

# Middleware, die die Tags "script_duration" und "page_msg" ersetzt
from PyLucid.middlewares import replacer
app = replacer.AddCode(app) # Middleware, für addCode
app = replacer.Replacer(app)





if __name__ == '__main__':
    # Eine Aufwendigere Variante, damit der Standalone-Entwicklungsserver
    # auch funktioniert, s. http://trac.pocoo.org/ticket/87
    def start():
        host = "localhost"
        port = 8080
        print "\n", "="*79
        print "Starting development server on: '%s:%s'...\n" % (host, port)

        # with 'debugged application':
        from colubrid.debug import DebuggedApplication
        global app
        app = DebuggedApplication(app)

        # usind the new wsgiref (from Python 2.5)
        from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
        server = WSGIServer((host, port), WSGIRequestHandler)
        server.set_app(app)
        server.serve_forever()

    from colubrid import reloader
    reloader.main(start, [])

#~ if __name__ == '__main__':
    #~ print "\n", "="*79, "\nStarting local test server...\n"

    #~ # with 'debugged application':
    #~ from colubrid.debug import DebuggedApplication
    #~ app = DebuggedApplication(app)

    #~ from colubrid.server import execute
    #~ execute(app, debug=True, reload=True)
