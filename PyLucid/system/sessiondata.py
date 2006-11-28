#!/usr/bin/python
# -*- coding: UTF-8 -*-


"""
obsolete???
"""



__version__ = "v0.1"

__history__ = """
v0.1
    - Code cleanup
    - CGIdata used UserDict
v0.0.5
    - Fehlerabfrage bei convert_types() erweitert
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
import os, sys, cgi, urllib, UserDict
from socket import getfqdn



class CGIdata(UserDict.UserDict):
    """
    Wertet die POST- und GET-Daten aus. Macht diese als dict verfügbar.
    Dabei werden alle Zahlen mit int() konvertiert.
    Fügt in's dict noch client_ip und client_domain ein (Methode get_client_info)
    """
    def __init__(self, PyLucid):
        """
        CGIdata ist eine abgeleitetes Dictionary und kann
        somit wie ein Dict angesprochen werden.
        """
        self.page_msg   = PyLucid["page_msg"]

        self.data = {} # Dict in dem die CGIdaten gespeichert werden

        self.get_CGIdata() # CGI-Daten ermitteln

        self.convert_types()

        self.get_client_info() # Client Info's ins CGI-data-dict packen

    def get_CGIdata(self):
        """
        sammelt POST und GET Daten zusammen
        Er wird zuerst cgi.FieldStorage abgefragt und dann erst den QUERY_STRING, weil
        cgi.FieldStorage automatisch ein urllib.unquote() durchführt, aber die Original
        Daten gebraucht werden, die im QUERY_STRING noch drin stecken.
        Das ist wichtig für Seitennamen mit "Sonderzeichen" wie "/" ;)

        Normalerweise reicht ein cgi.FieldStorage(keep_blank_values=1) und die
        os.environ['QUERY_STRING'] Auswertung könnte man sich sparen. Aber das
        ganze funktioniert nicht mit Python v2.2.1 :( Also wird's doch umständlich
        gemacht ;)
        """

        if "CONTENT_LENGTH" in os.environ:
            # Ist nur vorhanden, wenn der Client POST Daten schickt.
            length = int(os.environ["CONTENT_LENGTH"])
            if length>65534:
                print "Content-type: text/html; charset=utf-8\r\n"
                print "<h1>Error: Too much POST/GET content!</h1>"
                print "Content length = %s" % length
                sys.exit()
            #~ else:
                #~ self.page_msg("Content length = %s" % length)

            FieldStorageData = cgi.FieldStorage()

            # POST Daten auswerten
            for i in FieldStorageData.keys():
                self.data[i] = FieldStorageData.getvalue(i)

        if 'QUERY_STRING' in os.environ:
            # GET URL-Parameter parsen
            for item in os.environ['QUERY_STRING'].split("&"):
                size = len(item)
                if size>10000:
                    self.page_msg("CGI Error, GET Parameter size overload: '%s...'" % item[:10])
                    continue

                item = item.split("=",1)
                if len(item)==1:
                    if item[0]!="":
                        self.data[ item[0] ] = ""
                else:
                    self.data[ item[0] ] = item[1]

        #~ self.page_msg(self.data)

    def convert_types(self):
        """
        Versucht Zahlen von str nach int zu convertieren
        """
        for k,v in self.data.iteritems():
            try:
                self.data[k] = int(v)
            except:
                pass


    def get_client_info(self):
        """
        Client Informationen festhalten. Ist u.a. für's SQL-logging interessant.
        """
        if not os.environ.has_key("REMOTE_ADDR"):
            self.data["client_ip"] = "unknown"
            self.data["client_domain"] = "unknown"
            return

        self.data["client_ip"] = os.environ["REMOTE_ADDR"]
        try:
            self.data["client_domain"] = getfqdn(self.data["client_ip"])
        except Exception, e:
            self.data["client_domain"] = "unknown: '%s'" % e

    #______________________________________________________________________________

    def debug(self):
        #~ print "Content-type: text/html\n"
        #~ print "<pre>"
        #~ for k,v in self.data.iteritems():
            #~ self.page_msg("%s - %s" % (k,v))
        #~ print cgi.FieldStorage(keep_blank_values=True)
        #~ print "REQUEST_URI:",os.environ["REQUEST_URI"]
        #~ print "</pre>"
        import cgi

        import inspect
        # PyLucid's page_msg nutzen
        self.page_msg("-"*30)
        self.page_msg(
            "CGIdata Debug (from '...%s' line %s):" % (inspect.stack()[1][1][-20:], inspect.stack()[1][2])
        )

        self.page_msg("-"*30)
        for k,v in self.data.iteritems():
            self.page_msg("%s - %s" % (k, cgi.escape(str(v))))
        self.page_msg("FieldStorage:", cgi.FieldStorage(keep_blank_values=True))
        try:
            self.page_msg('os.environ["QUERY_STRING"]:', os.environ['QUERY_STRING'])
        except:
            pass
        try:
            self.page_msg('os.environ["REQUEST_URI"]:', os.environ["REQUEST_URI"])
        except:
            pass
        try:
            self.page_msg('os.environ["CONTENT_LENGTH"]:', os.environ["CONTENT_LENGTH"])
        except:
            pass
        self.page_msg("-"*30)








