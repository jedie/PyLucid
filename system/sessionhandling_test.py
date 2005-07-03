#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Ein kleiner Test f¸r den Session-Handler (sessionhandling.py)
by JensDiemer.de
"""

__version__ = "v0.0.1"

__history__ = """
v0.0.1
    - erste Version
"""

import cgitb;cgitb.enable()
import sys, os, cgi
import MySQLdb as DBlib


import sessionhandling

dbconf = {
    "dbHost"            : "localhost",
    "dbDatabaseName"    : '',
    "dbUserName"        : '',
    "dbPassword"        : '',
}
from config import dbconf

#~ sql_tablename = "lucid_session_data"
sql_tablename = "session_demo"
log_typ = "sessionhandling_DEMO"

class db:
    """
    Minimalversion einer DB-Klasse, die fÌ≤†den SessionHandler benÁµ©gt wird.
    """
    def __init__( self ):
        self.connect()

    def connect( self ):
        self.connection = DBlib.connect(
            dbconf["dbHost"],
            dbconf["dbUserName"],
            dbconf["dbPassword"],
            dbconf["dbDatabaseName"]
        )
        self.cursor = self.connection.cursor()


import SQL_logging

class sessiontest:
    def __init__( self ):
        Mydb = db()
        self.log = SQL_logging.log( Mydb.cursor )
        self.log.set_typ( log_typ )
        self.session = sessionhandling.sessionhandler( Mydb.cursor, sql_tablename, self.log )
        self.session.log_typ = log_typ
        #~ self.session = sessionhandler( Mydb.cursor, sql_tablename )

        self.cgidata = self.getCGIdata()

        if self.cgidata.has_key("Submit"):
            if self.cgidata["Submit"] == "add Data":

                if self.session.ID == False:
                    # Gibt noch keine Session -> er√∂ffne eine
                    self.session.makeSession()
                    self.print_html_head()

                    self.log.client_sID = self.session.ID
                    self.log.write( "Session erstellt." )

                else:
                    self.print_html_head()

                # Session Daten speichern
                self.log.client_sID = self.session.ID
                self.log.write( "Add Data zu Session" )

                try:
                    name = self.cgidata["name"]
                    data = self.cgidata["data"]
                    self.session[name] = data
                    self.session.update_session() # Schreibt session-Daten in die DB
                except KeyError:
                    print "<strong>Form error! Please fill out all fields.</strong>"

        elif self.cgidata.has_key("delete"):
            # LogOut
            self.log.write( "delete Session / LogOut" )
            self.session.delete_session()
            self.print_html_head()
        else:
            if self.session.ID != False:
                # Existierende Session laden
                self.log.client_sID = self.session.ID
                self.log.write( "Session reload" )

            self.print_html_head()

        print "<hr />"
        print "<strong>Session-Data:</strong>"
        print "<pre>"
        #~ print "cgi_daten.....:", self.cgidata
        print "Session-ID....:", self.session.ID
        print "Session-Data..:", self.session
        #~ print "l√§nge in DB...: %sBytes" % self.session.RAW_session_data_len
        print "</pre>"
        print "<hr />"

        print "<strong>Test:</strong>"

        print '<form name="data" method="post" action=""><p>'
        print 'name:<input name="name" type="text" value="">'
        print 'data:<input name="data" type="text" value="">'
        print '<input type="submit" name="Submit" value="add Data" />'
        print '</p></form>'
        print '| <a href="?">reload Page</a> | <a href="?delete=1">delete Session/LogOut</a> |'
        print "<hr />"

        print "<strong>Your DB-Log-Data:</strong>"

        print "<pre>"
        print self.log.get_by_IP(
                os.environ["REMOTE_ADDR"],
                log_typ="sessionhandling_DEMO",
                plaintext=True
            )
        print "</pre>"

        print "<hr />"

        print "<strong>Infromation:</strong>"
        print "<pre>"
        print "Dies ist ein Test f√ºr das Python-SQL-Session handling."
        print
        print "Vorgehensweise:"
        print "1. Formular ausf√ºllen mit irgendwelchen Werten"
        print "2. reload klicken, auch mehrmals"
        print "3. Die vorherigen Daten sollten nun per Session-Handling aus der DB kommen"
        print "4. mehr Daten eingeben oder LogOut durchf√ºhren"
        print "</pre>"
        print '<p>by: <a href="http://www.jensdiemer.de">Jens Diemer</a><br />'
        print "(steht unter GPL-License)</p>"

        print '</body></html>'


    def getCGIdata( self ):
        "CGI-POST Daten auswerten"
        data = {}
        FieldStorageData = cgi.FieldStorage()
        for i in FieldStorageData.keys(): data[i] = FieldStorageData.getvalue(i)
        return data

    def print_html_head( self ):
        print "Content-type: text/html\n"
        print '<?xml version="1.0" encoding="UTF-8"?>'
        print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">'
        print '<html xmlns="http://www.w3.org/1999/xhtml">'
        print '<head>'
        print '<title>JensDiemer.de - Index</title>'
        print '<meta name="Author"                    content="Jens Diemer" />'
        print '<meta http-equiv="Content-Type"        content="text/html; charset=utf-8" />'
        print '</head><body>'
        print '<h3>Python CGI-Cookie-SQL Session Handling DEMO</h3>'






if __name__ == "__main__":
    sessiontest()
















