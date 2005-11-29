#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Allgemeiner SQL-Logger
"""

__version__ = "v0.0.6"

__history__ = """
v0.0.6
    - Fehlerabfrage, wenn nicht in sql log table geschrieben werden kann
v0.0.5
    - Bug: Tabellenname (sql_tablename) war Hardcoded.
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

# Legt fest wie alt Log-Einträge max sein dürfen
# 3 Tage ==> 3Tage * 24Std * 60Min * 60Sec = 259200sec
enty_timeout_sec = 259200

sql_tablename = "log"

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
        self.db         = PyLucid["db"]
        self.tools      = PyLucid["tools"]
        self.CGIdata    = PyLucid["CGIdata"]
        self.page_msg   = PyLucid["page_msg"]

        # auf Default-Werte setzten
        # Nachdem eine Session erstellt wurde, werden diese Werte von index.py gesetzt
        self.client_sID         = "unknown"
        self.client_user_name   = "unknown"


    def check_type( self, type ):
        if type != False:
            return type

        import inspect
        # Den ersten Eintrag finden, der nicht aus dieser Datei stammt, denn
        # das ist der Eintrag, der einen Log-Einrag abgesetzt hat ;)
        for item in inspect.stack():
            filename = item[1].replace( "\\", "/" )
            filename = filename.split("/")[-1]
            if filename != "SQL_logging.py":
                return "%-20s line %3s" % (filename, item[2] )

        return type


    #________________________________________________________________________________________
    ## Log-Datei schreiben / verwalten

    def write( self, log_message, type=False, status="-1" ):
        "File like writing method"
        self.put( log_message, type, status )

    def __call__( self, log_message, type=False, status="-1" ):
        # Direkter Call-Aufruf zum schreiben
        self.put( log_message, type, status )

    def put( self, log_message, type=False, status="-1" ):
        "Schreib einen Eintag in die SQL-Log-Tabelle"

        type = self.check_type( type )

        # Alte Log-Einträge löschen
        self.delete_old_logs()

        try:
            self.db.insert(
                    table = "log", # Prefix wird bei db.insert eingefügt
                    data  = {
                        "timestamp" : self.tools.convert_time_to_sql( time.time() ),
                        "sid"       : self.client_sID,
                        "user_name" : self.client_user_name,
                        "ip"        : self.CGIdata["client_ip"],
                        "domain"    : self.CGIdata["client_domain"],
                        "message"   : log_message,
                        "typ"       : type,
                        "status"    : status,
                    }
                )
        except Exception, e:
            self.page_msg("Can't write to SQL log table: %s" % e)

    def delete_old_logs( self ):
        "Löscht veraltete Log-Einträge in der DB"

        SQLcommand  = "DELETE FROM %s%s" % ( dbconf["dbTablePrefix"], sql_tablename )
        SQLcommand += " WHERE timestamp < %s"

        current_timeout = time.time() - enty_timeout_sec

        self.db.cursor.execute(
            SQLcommand,
            ( current_timeout, )
        )

    #________________________________________________________________________________________
    ## Log-Datei lesen

    def get_last_logs( self, limit=10 ):
        """ Liefert die letzten >limit< Logeinträge zurück """
        return self.db.select(
            select_items    = ["timestamp", "sid", "user_name", "ip", "domain", "message","typ","status"],
            from_table      = sql_tablename,
            order           = ("id","DESC"),
            limit           = (0,limit)
        )

    def debug_last(self):
        import inspect
        self.page_msg(
            "Log Debug (from '%s' line %s):" % (inspect.stack()[1][1][-20:], inspect.stack()[1][2])
        )
        for item in self.get_last_logs(limit=10):
            self.page_msg(item["timestamp"], item["sid"], item["message"])



