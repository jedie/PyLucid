#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Allgemeiner CGI-Session-handler
auf Cookie + SQL basis

benötigte SQL-Tabelle:
-------------------------------------------------------
CREATE TABLE IF NOT EXISTS `lucid_session_data` (
  `session_id` varchar(32) NOT NULL default '',
  `timestamp` int(15) NOT NULL default '0',
  `ip` varchar(15) NOT NULL default '',
  `domain_name` varchar(50) NOT NULL default '',
  `session_data` text NOT NULL,
  PRIMARY KEY  (`session_id`),
  KEY `session_id` (`session_id`)
) COMMENT='Python-SQL-CGI-Sessionhandling';
-------------------------------------------------------

Information
===========
Session-Handling ermöglicht es, Variablen (ein dict) zwischen verschiedene
Anfragen hinweg pro User zu speichern.
Damit ist es einfacher Web-Applikationen in Python-CGI zu schreiben, ohne Daten
ständig per Formular weiter zu transportieren ;)

Ein Besucher der Webseite wird mit einer eindeutigen Session-ID per Cookie gekennzeichnet.
Variablen werden in ein Dictioary gespeichert. Dieses Dict wird mittelt pickle serialisiert
und zusammen mit der Session-ID in die SQL-Datenbank gespeichert.
Beim nächsten Aufruf stehen die speicherten Daten wieder zu verfügung.

Grober Ablauf:
==============

session = sessionhandling.sessionhandler( mySQLdb.cursor, sql_tablename, file_like_log )
# mySQLdb.cursor => Cursor-Objekt der Datenbank-API
# sql_tablename  => Name der Tabelle, in der die Sessiondaten verwaltet werden soll (s.SQL-Dump oben)
# file_like_log  => Ein LOG-Objekt, welches eine write()-Methode besitzt

# Erst nach der Instanzierung kann der HTML-Header an den Client geschickt werden
print "Content-type: text/html\n"

if self.session.ID == False:
    # Keine Session vorhanden
else:
    # eine Session ist vorhanden
    if aktion == "LogOut":
        # ein LogOut wird durchgeführt
        self.session.delete_session()
    else:
        # Schreibe Informationen in das Dictionary
        self.session[key] = data
        self.session["UserName"] = username

    # Sessiondaten in die Datenbank schreiben
    self.session.update_session()

    # Session-Daten anzeigen:
    print self.session


Hinweis
-------
Da das Sessionhandling auf Cookies basiert, ist folgendes wichtig:
For dem Instanzieren der sessionhandler-Klasse darf noch kein Header (print "Content-type: text/html\n") an
den Client geschickt worden sein! Ansonsten zählt der Cookie-Print nicht mehr zum Header und wird im Browser
einfach nur angezeigt ;)
"""

__version__ = "v0.0.5"

__history__ = """
v0.0.5
    - Umstellung auf MySQLdb.cursors.DictCursor
v0.0.4
    - NEU: verbose_log: damit nicht die Log-Ausgaben zuviele sind ;)
v0.0.3
    - __delitem__() hinzugefügt, um Session daten auch wieder löschen zu können
v0.0.2
    - Fehlerbereinigt / verschönert
v0.0.1
    - erste Version
"""

import os, sys, md5, time, pickle
from socket import getfqdn
from Cookie import SimpleCookie


# Bestimmt den Log-Typ
log_typ = "sessionhandling"


class sessionhandler:
    """
    CGI-Session Handler
    used mySQL and Cookies

    by JensDiemer.de

    http://www.python-forum.de/viewtopic.php?p=19523#19523
    """
    def __init__ ( self, db_cursor, sql_tablename, log_fileobj, timeout_sec=1800, CookieName="session_id", verbose_log = False ):
        self.Cookie         = SimpleCookie()

        self.db_cursor      = db_cursor
        self.log            = log_fileobj

        self.sql_tablename  = sql_tablename
        self.timeout_sec    = timeout_sec
        self.CookieName     = CookieName
        self.verbose_log    = verbose_log

        self.set_default_values()
        self.detectSession()

    def set_default_values( self ):
        """
        Setzt Interne Session-Variable auf voreinstestellte 'keine-Session-vorhanden-Werte'
        benötigt von:
        self.__init__()
        self.delete_session()
        """
        self.client_IP          = "not available"
        self.client_domain_name = "not available"

        self.RAW_session_data_len   = -1

        self.ID = False # =False -> es existiert keine Session
        self.session_data = {}

    def detectSession( self ):
        "Prüft ob eine Session schon besteht"
        try:
            cookie_id = self.readCookie()
        except KeyError:
            # Es gibt kein Session-Cookie, also gibt es keine gültige Session
            self.deleteCookie()
            if self.verbose_log==True:
                self.log.write( "error;Cookie not in DB!" )
            return

        if cookie_id == "":
            self.status = "error;deleted Cookie found / Client not LogIn!"
            return

        if len( cookie_id ) != 32:
            # Mit dem Cookie stimmt wohl was nicht ;)
            self.deleteCookie()
            self.log.write( "error;wrong Cookie len: %s !" % len( cookie_id ) )
            return

        try:
            self.read_session_data( cookie_id )
        except Exception, e:
            # Es gibt keine Daten zur ID / Falsche Daten vorhanden
            self.deleteCookie()
            self.log.write( "error;read_session error: %s" % e )
            return

        # Aktualisiert Cookie
        self.writeCookie( self.ID )
        #~ self.log.write( "OK;found Session." )

    def read_session_data( self, cookie_id ):
        "Liest Session-Daten zur angegebenen ID aus der DB"
        DB_data = self.read_from_DB( cookie_id )

        current_IP, current_domain_name = self.get_client_info()
        if not (DB_data["ip"] == current_IP) and (DB_data["domain_name"] == current_domain_name):
            self.delete_session()
            raise IndexError, "Wrong client IP / domain name: %s-%s / %s-%s" % (
                DB_data["ip"], current_IP, DB_data["domain_name"], current_domain_name
            )

        # Session ist OK

        self.ID                 = cookie_id
        self.client_IP          = current_IP
        self.client_domain_name = current_domain_name
        self.session_data       = DB_data["session_data"]

    def makeSession( self ):
        """
        Startet eine Session
        noch darf kein "Content-type" zum Browser geschickt worden sein
        (sonst funktioniert das schreiben eines Cookies nicht mehr!)
        """
        # Schreibt ID-Cookie
        session_id = self.write_session_cookie()

        # Stellt Client Info's fest
        self.client_IP, self.client_domain_name = self.get_client_info()

        # Speichert den User in der SQL-DB
        self.insert_session( session_id )

        # Aktualisiert ID global
        self.ID = session_id

    def write_session_cookie( self ):
        "Generiert eine Session ID und speichert diese als Cookie"
        session_id = md5.new( str(time.time()) + os.environ["REMOTE_ADDR"] ).hexdigest()
        self.writeCookie( session_id )
        return session_id

    def get_client_info( self ):
        """
        Information vom Client feststellen
        wird von read_session_data() und makeSession() verwendet
        """
        IP          = os.environ["REMOTE_ADDR"]
        domain_name = getfqdn( IP )
        return IP, domain_name

    ####################################################
    # Allgemeine Cookie-Funktionen

    def readCookie( self ):
        "liest Cookie"
        self.Cookie.load(os.environ["HTTP_COOKIE"])
        return self.Cookie[self.CookieName].value

    def writeCookie( self, Text, expires=None ):
        "speichert Cookie"
        if expires==None: expires=self.timeout_sec
        self.Cookie[self.CookieName] = Text
        self.Cookie[self.CookieName]["path"] = "/"
        self.Cookie[self.CookieName]["expires"] = expires
        # Cookie an den Browser "schicken"
        print self.Cookie[self.CookieName]

    def deleteCookie( self ):
        self.writeCookie( "" , 0)

    ####################################################
    # Allgemeine SQL-Funktionen

    def insert_session( self, session_id ):
        "Eröffnet eine Session"
        self.delete_old_sessions() # L�schen veralteter Sessions in der DB

        session_data = pickle.dumps( self.session_data )
        self.RAW_session_data_len = len( session_data )

        SQLcommand  = " INSERT INTO %s" % self.sql_tablename
        SQLcommand += " ( `session_id` , `timestamp` , `ip` , `domain_name` , `session_data` )"
        SQLcommand += " VALUES (%s, %s, %s, %s, %s);"

        self.db_cursor.execute(
            SQLcommand,
            ( session_id, time.time(), self.client_IP, self.client_domain_name, session_data )
        )
        self.log.write( "OK;created Session." )

    def update_session( self ):
        "Aktualisiert die Session-Daten"
        self.delete_old_sessions() # L�schen veralteter Sessions in der DB

        session_data = pickle.dumps( self.session_data )
        self.RAW_session_data_len = len( session_data )

        SQLcommand  = " UPDATE %s" % self.sql_tablename
        SQLcommand += " SET session_data=%s, timestamp=%s"
        SQLcommand += " WHERE session_id=%s"

        self.db_cursor.execute(
            SQLcommand,
            ( session_data, time.time(), self.ID )
        )
        if self.verbose_log == True:
            self.log.write( "OK;update Session." )


    def read_from_DB( self, session_id ):
        "Liest Sessiondaten des Users mit der >session_id<"
        self.delete_old_sessions() # L�schen veralteter Sessions in der DB

        SQLcommand  = " SELECT session_id, timestamp, ip, domain_name, session_data"
        SQLcommand += " FROM %s" % self.sql_tablename
        SQLcommand += " WHERE session_id=%s"

        self.db_cursor.execute( SQLcommand, (session_id,) )
        DB_data = self.db_cursor.fetchall()[0]

        self.RAW_session_data_len = len( DB_data["session_data"] )

        DB_data["session_data"] = pickle.loads( DB_data["session_data"] )

        return DB_data


    def delete_old_sessions( self ):
        "Löscht veraltete Sessions in der DB"
        SQLcommand  = "DELETE FROM %s" % self.sql_tablename
        SQLcommand += " WHERE timestamp < %s"

        current_timeout = time.time() - self.timeout_sec

        try:
            self.db_cursor.execute(
                SQLcommand,
                ( current_timeout, )
            )
        except Exception, e:
            print "Content-type: text/html\n"
            print "Delete Old Session error: %s" % e
            sys.exit()

    def delete_session( self ):
        "Löscht die aktuelle Session"
        if self.ID == False:
            self.status = "OK;Client is LogOut, can't LogOut a second time :-)!"
            return

        self.deleteCookie()

        SQLcommand  = "DELETE FROM %s" % self.sql_tablename
        SQLcommand += " WHERE session_id=%s"

        self.db_cursor.execute( SQLcommand, (self.ID,) )
        self.db_cursor.fetchall()

        oldID = self.ID

        # Interne-Session-Variablen rücksetzten
        self.set_default_values()

        self.status = "OK;delete Session data / LogOut for '%s'" % oldID

    ####################################################
    # Funktionen zum abfragen/setzten der Session-Daten

    def __setitem__( self, key, value):
        "Ermöglicht das direkte setzten der Session-Daten"
        self.session_data[key] = value

    def __str__(self):
        "Liefer Session-Daten als String zurück, also: retrun str(dict)"
        return str( self.session_data )

    def __getitem__( self, key ):
        return self.session_data[key]

    def __delitem__( self, key ):
        del self.session_data[key]

    def has_key( self, key ):
        return self.session_data.has_key(key)

    def iteritems( self ):
        return self.session_data.iteritems()

    def debug( self ):
        "Zeigt alle Session Informationen an"
        print "Content-type: text/html\n"
        print "<h1>Session Debug:</h1>"
        print "<pre>"
        for k,v in self.session_data.iteritems():
            print k,"-",v
        print "</pre><hr>"






