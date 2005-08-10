#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Allgemeiner SQL-Logger
"""

__version__ = "v0.0.4"

__history__ = """
v0.0.4
    - Mittels *log_message bei put() werden nun auch Komma-getrennte Log's aufgenommen
v0.0.3
    - DEL: Es gibt kein log_typ mehr
    - Nutzt Zeitumwandlung aus PyLucid["tools"]
v0.0.2
    - Anpassung an PyLucid's SQL-Klasse
v0.0.1
    - erste Version
"""

import time, os
from socket import getfqdn

# Legt fest wie alt Log-Eintr�ge max sein d�rfen
# 3 Tage ==> 3Tage * 24Std * 60Min * 60Sec = 259200sec
enty_timeout_sec = 259200

sql_tablename = "lucid_log"


dbconf = {
    "dbHost"            : "localhost",
    "dbDatabaseName"    : '',
    "dbUserName"        : '',
    "dbPassword"        : '',
}
# dbconfig mit abgespeicherten DB-Config Daten überschreiben
from config import dbconf



class log:
    """
    Allgemeine SQL-Logging Klasse
    """
    def __init__ ( self, PyLucid ):
        self.db     = PyLucid["db"]
        self.tools  = PyLucid["tools"]

        # auf Default-Werte setzten
        self.client_sID         = False
        self.client_user_name   = False
        self.client_ip          = False
        self.client_domain      = False

    def check_client_data( self ):
        "Automatisches setzten von Client-Daten, wenn nicht schon geschehen"
        if not os.environ.has_key("REMOTE_ADDR"):
            return

        if (self.client_ip == "-1") or (self.client_ip != os.environ["REMOTE_ADDR"]):
            self.client_ip = os.environ["REMOTE_ADDR"]
            try:
                self.client_domain = getfqdn( self.client_ip )
            except Exception, e:
                self.client_domain = "can't detect: %s" % e

    #________________________________________________________________________________________
    ## Log-Datei schreiben / verwalten

    def write( self, log_message ):
        "File like writing method"
        self.put( log_message )

    def __call__( self, *log_message ):
        # Direkter Call-Aufruf zum schreiben
        self.put( *log_message )

    def put( self, *log_message ):
        "Schreib einen Eintag in die SQL-Log-Tabelle"
        self.check_client_data()

        # Alte Log-Einträge löschen
        self.delete_old_logs()

        log_message = " ".join( [str(i) for i in log_message] )

        self.db.insert(
                table = "log",
                data  = {
                    "timestamp" : self.tools.convert_time_to_sql( time.time() ),
                    "sid"       : self.client_sID,
                    "user_name" : self.client_user_name,
                    "ip"        : self.client_ip,
                    "domain"    : self.client_domain,
                    "message"   : log_message,
                }
            )

    def delete_old_logs( self ):
        "Löscht veraltete Log-Einträge in der DB"

        SQLcommand  = "DELETE FROM %s" % sql_tablename
        SQLcommand += " WHERE timestamp < %s"

        current_timeout = time.time() - enty_timeout_sec

        self.db.cursor.execute(
            SQLcommand,
            ( current_timeout, )
        )

    #________________________________________________________________________________________
    ## Log-Datei lesen

    #~ def get_by_IP( self, IP, log_typ=None, plaintext = False ):
        #~ "Alle Log-Eintr�ge von der angegebenen IP-Adresse"

        #~ if log_typ == None:
            #~ SQLcommand  = " SELECT timestamp, typ, sid, user_name, ip, domain, message"
            #~ SQLcommand += " FROM %s" % sql_tablename
            #~ SQLcommand += " WHERE ip=%s"
        #~ else:
            #~ SQLcommand  = " SELECT timestamp, sid, user_name, ip, domain, message"
            #~ SQLcommand += " FROM %s" % sql_tablename
            #~ SQLcommand += " WHERE ( ip=%s and typ=%s )"

        #~ SQLcommand += " ORDER BY `timestamp` DESC"
        #~ SQLcommand += " LIMIT 0,10"

        #~ if log_typ == None:
            #~ self.db_cursor.execute( SQLcommand, (IP,) )
        #~ else:
            #~ self.db_cursor.execute( SQLcommand, (IP,log_typ) )

        #~ DB_data = self.db_cursor.fetchall()

        #~ if plaintext == False:
            #~ return DB_data

        #~ result = ""
        #~ for line in DB_data:
            #~ timestamp = line[0]
            #~ info = line[1:]
            #~ result += self.tools.convert_date_from_sql( timestamp )
            #~ result += " - "
            #~ result += ", ".join( [str(i) for i in info] )
            #~ result += "\n"
        #~ return result

    def get_last_logs( self, limit=10 ):
        """ Liefert die letzten >limit< Logeinträge zurück """
        return self.db.select(
            select_items    = ["timestamp", "sid", "user_name", "ip", "domain", "message"],
            from_table      = "log",
            order           = ("id","DESC"),
            limit           = (0,limit)
        )




