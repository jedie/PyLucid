#!/usr/bin/python
# -*- coding: UTF-8 -*-



__version__ = "v0.0.4"

__history__ = """
v0.0.4
    - detect_page() zur index.py verschoben
v0.0.3
    - Mehrfach connection vermieden.
v0.0.2
    - Die Daten werden nun schon mal vorverarbeitet
    - os.environ['QUERY_STRING'] wird mit urllib.unquote() verarbeitet
v0.0.1
    - erste Version
"""


# Python-Basis Module einbinden
import os, cgi, urllib

# PyLucid Module
import config

if config.system.page_msg_debug:
    import inspect



#~ from config import dbconf


# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"



class CGIdata:
    """
    Wertet die POST- und GET-Daten aus.
    Macht sich als dict verfügbar.
    Stellt fest, welche Seite abgefunden werden soll
    """
    def __init__( self, PyLucid ):
        """
        CGIdata ist eine abgeleitetes Dictionary und kann
        somit wie ein Dict angesprochen werden.
        """
        self.page_msg   = PyLucid["page_msg"]

        self.data = {} # Dict in dem die CGIdaten gespeichert werden

        self.get_CGIdata() # CGI-Daten ermitteln

        self.convert_types()

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

    def convert_types( self ):
        for k,v in self.data.iteritems():
            try:
                self.data[k] = int( v )
            except ValueError:
                pass

    #______________________________________________________________________________
    # Methoden um an die Daten zu kommen ;)

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

    def keys( self ):
        return self.data.keys()

    def __len__( self ):
        return len( self.data )

    #______________________________________________________________________________

    def error( self, txt1, txt2="" ):
        print "Content-type: text/html\n"
        print "<h1>Error: %s</h1>" % txt1
        print txt2
        import sys
        sys.exit()

    def debug( self ):
        #~ print "Content-type: text/html\n"
        #~ print "<pre>"
        #~ for k,v in self.data.iteritems():
            #~ self.page_msg( "%s - %s" % (k,v) )
        #~ print cgi.FieldStorage( keep_blank_values=True )
        #~ print "REQUEST_URI:",os.environ["REQUEST_URI"]
        #~ print "</pre>"
        import cgi
        self.page_msg( "CGIdata Debug:" )
        self.page_msg( "-"*30 )
        for k,v in self.data.iteritems():
            self.page_msg( "%s - %s" % ( k, cgi.escape(str(v)) ) )
        self.page_msg( "FieldStorage:", cgi.FieldStorage( keep_blank_values=True ) )
        try:
            self.page_msg( 'os.environ["QUERY_STRING"]:', os.environ['QUERY_STRING'] )
        except:
            pass
        try:
            self.page_msg( 'os.environ["REQUEST_URI"]:', os.environ["REQUEST_URI"] )
        except:
            pass
        self.page_msg( "-"*30 )



##_______________________________________________________________________________________




class page_msg:
    """
    Kleine Klasse um die Seiten-Nachrichten zu verwalten
    page_msg wird in index.py den PyLucid-Objekten hinzugefugt.
    mit PyLucid["page_msg"]( "Eine neue Nachrichtenzeile" ) wird Zeile
    für Zeile Nachrichten eingefügt.
    Die Nachrichten werden ganz zum Schluß in der index.py in die
    generierten Seite eingeblendet. Dazu dient der Tag <lucidTag:page_msg/>
    """
    def __init__( self ):
        if config.system.page_msg_debug:
            self.data = "<p>[config.system.page_msg_debug = True!]</p>"
        else:
            self.data = ""

    def __call__( self, *msg ):
        """ Fügt eine neue Zeile mit einer Nachricht hinzu """
        if config.system.page_msg_debug:
            #~ for line in inspect.stack(): self.data += "%s<br/>" % str( line )
            self.data += "...%s line %s: " % (inspect.stack()[1][1][-20:], inspect.stack()[1][2] )

        self.data += "%s <br/>" % " ".join( [str(i) for i in msg] )










if __name__ == "__main__":
    page_name = "/Programmieren/Python/PyLucid"
    #~ page_name = "/Programmieren"
    page_name = page_name.split("/")[1:]
    #~ for name in page_name:

    print page_name












