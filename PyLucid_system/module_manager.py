#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Manager

# by jensdiemer.de (steht unter GPL-License)


"""

__version__="0.0.4"

__history__="""
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
    def __init__( self, PyLucid_objects ):
        self.PyLucid_objects    = PyLucid_objects
        self.session            = PyLucid_objects["session"]
        self.log                = PyLucid_objects["log"]

        self.modul_data = {}

    def read_module_info( self, package_name ):
        """Liest die Modul-Informationen aus dem >package_name< ein"""
        MyPackage_info = package_info()
        module_list = MyPackage_info.get_package_names( package_name )

        #~ print "Content-type: text/html\n"
        #~ print "<pre>"

        for module_name in module_list:
            #~ print "XXX",package_name, module_name,"XXX\n"
            try:
                module_data = MyPackage_info.get_module_data( package_name, module_name )
            except AttributeError:
                # module_info existiert nicht
                continue
            #~ print "YYY"

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

    def start_module( self, module_data ):
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
        try:
            result_page_data = module.PyLucid_action( self.PyLucid_objects )
        except Exception, e:
            return "Modul '%s.%s' Error: %s" % (
                module_data['package_name'], module_data['module_name'], e
            )

        # Letzte Aktion festhalten
        self.session["last_action"] = module_data['module_name']

        return result_page_data

    #_________________________________________________________________________________
    # Debugging

    def debug( self ):
        """Für Debugging Zwecke werden alle Daten angezeigt"""
        print "Content-type: text/html\n"
        print "<h1>Modul Manager Debug:</h1>"
        print "<pre>"
        for order,data in self.modul_data.iteritems():
            print order
            for k,v in data.iteritems():
                print "\t%s - %s" % (k,v)
            print "-"*80
        print "</pre>"



#~ if __name__ == "__main__":
    #~ mm = module_manager()
    #~ mm.parse_modules()
    #~ mm.debug()