#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Manager

# by jensdiemer.de (steht unter GPL-License)


"""

__version__="0.0.7"

__history__="""
v0.0.7
    - NEU: Module können nun auch nur normale print Ausgaben machen, die dann in die
        Seite "eingeblendet" werden sollen
    - NEU: "direct_out"-Parameter, wird z.B. für das schreiben des Cookies in user_auth.py
        verwendet. Dann werden print-Ausgaben nicht zwischengespeichert.
v0.0.6
    - Fehler beim import sehen nur Admins
v0.0.5
    - Debug mit page_msg
v0.0.4
    - "must_login" und "must_admin" muß nun in jedem Modul definiert worden sein.
    - Fehlerabfrage beim Module/Aktion starten
v0.0.3
    - NEU: start_module()
v0.0.2
    - Großer Umbau :)
v0.0.1
    - erste Version
"""


import sys, os, glob
import cgitb;cgitb.enable()


# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"



class package_info:
    def get_package_names( self, package_name ):
        """Liefert eine Liste aller Dateinamen eines Paketes zurück"""
        try:
            package_path = __import__( package_name ).__path__[0]
        except:
            return []
        package_list = []
        path = os.path.join( package_path, "*.py" )

        for filename in glob.glob( path ):
            #~ print filename
            path,name = os.path.split( filename )
            name,ext = os.path.splitext( name )
            if name == "__init__":
                continue
            package_list.append( name )
        return package_list

    def get_module_data( self, package_name, module_name ):
        """Daten aus der pseudo Klasse 'module_info' holen"""
        return __import__(
            "%s.%s" % (package_name,module_name),
            globals(), locals(),
            ["module_info"]
        ).module_info.data


class module_manager:
    def __init__( self, PyLucid ):
        self.PyLucid    = PyLucid
        self.session            = PyLucid["session"]
        #~ self.session.debug()
        self.log                = PyLucid["log"]
        self.config             = PyLucid["config"]
        self.page_msg           = PyLucid["page_msg"]

        self.modul_data = {}

    def read_module_info( self, package_name ):
        """Liest die Modul-Informationen aus dem >package_name< ein"""

        #~ print "Content-type: text/html\n"
        #~ print "<pre>"

        MyPackage_info = package_info()
        module_list = MyPackage_info.get_package_names( package_name )

        #~ self.page_msg( "Debug, ModulList: '%s'" % str(module_list) )

        for module_name in module_list:

            try:
                module_data = MyPackage_info.get_module_data( package_name, module_name )
            except Exception, e:
                # Fehler beim import
                if self.config.system.ModuleManager_import_error == True or \
                self.session.has_key("isadmin") and self.session["isadmin"] == True:
                    # Fehler nur anzeigen, wenn ein Administrator eingeloggt ist.
                    self.page_msg( "ModulManager error with module '%s.%s':<br/> - %s" % (
                            package_name,module_name,e
                        )
                    )
                continue

            for order,data in module_data.iteritems():
                if self.modul_data.has_key( order ):
                    # Fehler: Es dürfen keine zwei "order"-Kommandos existieren!
                    print "Content-type: text/html\n"
                    print "<h1>internal error!</h1>"
                    print "<h3>duplicate module/plugin orders:</h3>"
                    print "<p>duplicate order: '%s'<br/>" % order
                    print "Modul 1: ./%s/%s.py<br/>" % (
                        self.modul_data[order]["package_name"],
                        self.modul_data[order]["module_name"]
                    )
                    print "Modul 2: ./%s/%s.py</p>" % ( package_name,module_name )
                    sys.exit()

                # Daten mit module_name und package_name erweitern
                data["module_name"]  = module_name
                data["package_name"] = package_name

                # Daten speichern
                self.modul_data[order] = data

        # package_info()-Klasse komplett löschen
        del( MyPackage_info )

    #_________________________________________________________________________________
    # Spezielle angepasste PyLucid Funktionen

    def get_menu_data( self, section ):
        """Liefert alle Daten zu einer Menu-Sektion"""
        menu_data = {}

        for order,data in self.modul_data.iteritems():
            if data.has_key("section") and data["section"] == section:
                menu_data[order] = data

        return menu_data

    def get_orders( self ):
        """Informationen über alle URL Kommandos"""
        order_data = {}

        for order,data in self.modul_data.iteritems():
            order_data[order] = data

        return order_data

    def get_lucidTags( self ):
        """ Module die lucidTags bieten """
        result = {}
        for order,data in self.modul_data.iteritems():
            if data.has_key("lucidTag"):
                result[order] = data
        return result

    def get_lucidFunctions( self ):
        """ Module die lucidFunktions sind """
        result = {}
        for order,data in self.modul_data.iteritems():
            if data.has_key("lucidFunction"):
                result[order] = data
        return result

    def start_module( self, module_data, function_string=None ):
        """
        Starten eines Dynamischen Modules
        Wird benötigt für alle command-Befehle (aus der index.py) und
        für z.B. das SiteMap
        """
        def error( txt ):
            return "<p>Modul '%s.%s' Error: %s</p>" % (
                module_data['package_name'], module_data['module_name'], txt
            )

        # Rechteverwaltung 1: Muß der User eingeloggt sein? Ist er es?
        try:
            if (module_data['must_login'] == True) and (self.session.ID == False):
                return error("Your not login!")
        except KeyError:
            return error("Info 'must_login' not defined!")

        # Rechteverwaltung 2: Muß es ein Admin sein? Ist er es?
        try:
            if (module_data['must_admin']==True) and (self.session["isadmin"] == False):
                return error("You must be an admin to use this module!")
        except KeyError:
            return error("Info 'must_admin' not defined!")

        # Module wird importiert
        module = __import__(
            "%s.%s" % ( module_data['package_name'], module_data['module_name'] ),
            globals(), locals(),
            [ module_data['module_name'] ]
        )

        # Module/Aktion starten
        if self.config.system.ModuleManager_error_handling == True:
            # Fehler sollen abgefangen werden
            try:
                result_page_data = self.run_module( module, module_data, function_string )
            except Exception, e:
                return "Modul '%s.%s' Error: %s" % (
                    module_data['package_name'], module_data['module_name'], e
                )
        else:
            # Fehler sollen zu einem CGI-Traceback führen ( cgitb.enable() )
            result_page_data = self.run_module( module, module_data, function_string )

        # Letzte Aktion festhalten
        self.session["last_action"] = module_data['module_name']

        return result_page_data

    def run_module( self, module, module_data, function_string=None ):
        if (not module_data.has_key("direct_out")) or module_data["direct_out"] != True:
            # Alle Printausgaben zwischenspeichern
            self._redirect_stdout()

        if function_string != None:
            # Es ist eine lucidFunction mit einem "Parameter"
            result_page_data = module.PyLucid_action( self.PyLucid, function_string )
        else:
            # Muß eine normale lucidTag oder Commando sein
            result_page_data = module.PyLucid_action( self.PyLucid )

        if (not module_data.has_key("direct_out")) or module_data["direct_out"] != True:
            # Zwischengespeicherten print-Ausgaben abfragen
            redirect_data = self._get_redirect_data()
            if redirect_data != "":
                # Es wurden prints gemacht
                if result_page_data == None:
                    # Das Modul lieferte keine eigentlichen Ausgaben zurück, somit
                    # sind die print-Ausgaben die eigentlichen Daten
                    result_page_data = redirect_data
                else:
                    # Es wurden Ausgaben zurück gegeben, dann sind die print-Ausgaben
                    # wahrscheinlich nicht richtig, werden aber als page_msg angezeigt.
                    self.page_msg( redirect_data )

        return result_page_data

    def _redirect_stdout( self ):
        """
        stdout und stderr mit dem redirector() zwischenspeichern
        """
        self.oldstdout = sys.stdout
        self.oldstderr = sys.stderr

        self.out_redirect = redirector()

        sys.stdout = self.out_redirect
        sys.stderr = self.out_redirect

    def _get_redirect_data( self ):
        """
        liefert zwischengespeicherte Ausgaben zurück
        """
        sys.stdout = self.oldstdout
        sys.stderr = self.oldstderr
        return self.out_redirect.get()

    def start_lucidFunction( self, matchobj ):
        """
        Starten einer lucidFunction
        """
        Modulename = matchobj.group(1)
        function_string = matchobj.group(2)

        return self.start_module( self.modul_data[ Modulename ], function_string )

    #_________________________________________________________________________________
    # Debugging

    def debug( self ):
        """Für Debugging Zwecke werden alle Daten angezeigt"""
        self.page_msg( "Modul Manager Debug:" )
        self.page_msg( "-"*30 )
        for order,data in self.modul_data.iteritems():
            self.page_msg( ">>>",order )
            for k,v in data.iteritems():
                self.page_msg( "%s - %s" % (k,v) )
            self.page_msg( "-"*10 )
        self.page_msg( "-"*30 )


class redirector:
    def __init__( self ):
        self.data = ""

    def write( self, *txt ):
        self.data += " ".join([str(i) for i in txt])

    def flush( self ):
        return

    def get( self ):
        return self.data

#~ if __name__ == "__main__":
    #~ mm = module_manager()
    #~ mm.parse_modules()
    #~ mm.debug()