#!/usr/bin/python
# -*- coding: UTF-8 -*-

"Stores every Session Data in pseudoclasses"

__version__ = "v0.0.2"

__history__ = """
v0.0.2
    - Die Daten werden nun schon mal vorverarbeitet
    - os.environ['QUERY_STRING'] wird mit urllib.unquote() verarbeitet
v0.0.1
    - erste Version
"""


# Python-Basis Module einbinden
import os, cgi, urllib


# Eigene Module
import SQL



class CGIdata:
    """
    Wertet die POST- und GET-Daten aus.
    Macht sich als dict verfügbar.
    Stellt fest, welche Seite abgefunden werden soll
    """
    def __init__( self, db_handler = SQL.db(), detect_page = True ):
        """
        CGIdata ist eine abgeleitetes Dictionary und kann
        somit wie ein Dict angesprochen werden.
        """
        self.db = db_handler

        self.page_name_error = False

        self.data = {} # Dict in dem die CGIdaten gespeichert werden

        self.get_CGIdata() # CGI-Daten ermitteln

        if detect_page:
            self.detect_page() # Herrausfinden, welche Seite aktuell ist

    def get_CGIdata( self ):
        "sammelt POST und GET Daten zusammen"
        # Normalerweise reicht ein cgi.FieldStorage( keep_blank_values=1 ) und die
        # os.environ['QUERY_STRING'] Auswertung könnte man sich sparen. Aber das
        # ganze funktioniert nicht mit Python v2.2.1 :( Also wird's doch umständlich
        # gemacht ;)
        if os.environ.has_key('QUERY_STRING'):
            query_string = urllib.unquote( os.environ['QUERY_STRING'] )
            # print "<!-- %s -->" % os.environ['QUERY_STRING']
            # GET URL-Parameter parsen
            for i in query_string.split("&"):
                i=i.split("=")
                if len(i)==1:
                    if i[0]!="":
                        self.data[ i[0] ] = ""
                else:
                    self.data[ i[0] ] = i[1]

        FieldStorageData = cgi.FieldStorage()
        # POST Daten auswerten
        for i in FieldStorageData.keys():
            #~ print "<!-- %s-%s -->" % (i,FieldStorageData.getvalue(i))
            self.data[i] = FieldStorageData.getvalue(i)

    def detect_page( self ):
        "Findet raus welches die aktuell anzuzeigende Seite ist"

        if len( self.data ) == 0:
            # keine CGI-Daten vorhanden
            # `-> Keine Seite wurde angegeben -> default-Seite wird angezeigt
            self.set_default_page()
            return

        if self.data.has_key( "page_name" ):
            # Aufruf per <lucidFunction:IncludeRemote> mit der index.php
            page_name = self.data["page_name"]
            page_id = self.db.side_id_by_name( page_name )
            self.data["page_id"]    = page_id
            self.data["page_name"]  = page_name
            return

        if self.data.has_key( "command" ):
            # Ein internes Kommando (LogIn, EditPage ect.) wurde ausgeführt
            # `-> default-Seite wird angezeigt
            #~ self.set_default_page()
            return

        # Sucht in den URL-Parametern nach einem Seitennamen, um zu
        # bestimmen welches die aktuelle anzugeigenden Seite ist ;)
        for k,v in self.data.iteritems():
            if v == "":
                # Nur Key, kein Value -> könnte die Angabe der Seite sein
                page_id = self.db.side_id_by_name( k )

                if page_id != False:    # Richtigen Eintrag gefunden
                    page_name = k

                    # Gefunden Eintrag löschen, da er in der Form nutzlos ist
                    del( self.data[page_name] )

                    # Gefundene Seite als aktuelle Seite speichern
                    self.data["page_id"]    = page_id
                    self.data["page_name"]  = page_name
                    return

        # Es konnte keine Seite in URL-Parametern gefunden werden, also
        # wird die Standart-Seite genommen
        self.page_name_error = True
        self.set_default_page()

    def set_default_page( self ):
        "Setzt die default-Page als aktuelle Seite"
        page_id = self.db.preferences( "core", "defaultPageName" )["value"]
        try:
            page_name = self.db.side_name_by_id( page_id )
        except:
            print "Content-type: text/html\n"
            print "<h1>Error: Can't find default Page!</h1>"
            print "Check SQL-Tables!"
            import sys
            sys.exit()

        self.data["page_id"]    = page_id
        self.data["page_name"]  = page_name

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

    def debug( self ):
        print "Content-type: text/html\n"
        print "<pre>"
        for k,v in self.data.iteritems(): print "%s - %s" % (k,v)
        print "-"*80
        print cgi.FieldStorage( keep_blank_values=True )
        print "</pre>"
        #~ import sys
        #~ sys.exit()















