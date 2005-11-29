#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Verwaltung der Einstellungen
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.0.2"

__history__="""
v0.0.2
    - Fehlerabfrage beim Zugriff auf die SQL DB
v0.0.1
    - erste Version
"""




# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"





class preferences:
    """
    lucid-preferences aus Datenbank lesen und im preferences-Dict eintragen
    """

    def __init__( self, PyLucid_objects ):
        self.db = PyLucid_objects["db"]

        self.data = {} # In diese Dict werden die preferences gespeichert

        # Daten aus der SQL lesen und speichern
        self.read_from_sql()

    def read_from_sql( self ):
        """ Preferences aus der DB lesen und in self.data speichern """

        try:
            RAWdata = self.db.get_all_preferences()
        except Exception, e:
            print "Content-type: text/html; charset=utf-8\r\n\r\n"
            print "<h1>Error: Can't read preferences:</h1>"
            print e
            print "<p>(Did you install PyLucid correctly?)</p>"
            print "<hr><address>%s</address>" % __info__
            import sys
            sys.exit()
        #~ "section", "varName", "value"

        for line in RAWdata:
            # Die Values sind in der SQL-Datenbank als Type varchar() angelegt.
            # Doch auch Zahlenwerte sind gespeichert, die PyLucid doch lieber
            # auch als Zahlen sehen möchte ;)
            try:
                line["value"] = int( line["value"] )
            except ValueError:
                pass

            if not self.data.has_key( line["section"] ):
                # Neue Sektion
                self.data[ line["section"] ] = {}

            self.data[ line["section"] ][ line["varName"] ] = line["value"]


    #______________________________________________________________________________
    # allgemeine Methoden um an die Daten zu kommen ;)

    #~ def __getitem__( self, section, varName ):
        #~ return self.data[section][varName]
    def __getitem__( self, key ):
        return self.data[key]

    def iteritems( self ):
        return self.data.iteritems()

    def __setitem__( self, key, value ):
        self.data[key] = value

    def has_key( self, key ):
        return self.data.has_key( key )

    def __str__( self ):
        return str( self.data )

    #______________________________________________________________________________