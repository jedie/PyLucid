#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Allgemeiner SQL-Logger

SQL-Tabelle:
-------------------------------------------------------
CREATE TABLE IF NOT EXISTS `lucid_log` (
  `id` INT( 11 ) NOT NULL AUTO_INCREMENT ,
  `timestamp` INT( 15 ) NOT NULL ,
  `typ` VARCHAR( 50 ),
  `sid` VARCHAR( 50 ) DEFAULT '-1' NOT NULL,
  `ip` VARCHAR( 50 ),
  `domain` VARCHAR( 50 ),
  `message` VARCHAR( 255 ) NOT NULL ,
  PRIMARY KEY ( `id` )
) COMMENT='PyLucid - Logging';
-------------------------------------------------------
"""

__version__ = "v0.0.1"

__history__ = """
v0.0.1
    - erste Version
"""

import time, os
from socket import getfqdn

# Legt fest wie alt Log-Einträge max sein dürfen
# 3 Tage ==> 3Tage * 24Std * 60Min * 60Sec = 259200sec
enty_timeout_sec = 259200

sql_tablename = "lucid_log"


dbconf = {
    "dbHost"            : "localhost",
    "dbDatabaseName"    : '',
    "dbUserName"        : '',
    "dbPassword"        : '',
}
# dbconfig mit abgespeicherten DB-Config Daten Ã¼berschreiben
from config import dbconf



class log:
    """
    Allgemeine SQL-Logging Klasse
    """
    def __init__ ( self, db_cursor ):
        self.db_cursor = db_cursor

        # auf Default-Werte setzten
        self.client_sID         = "-1"
        self.client_ip          = "-1"
        self.client_domain      = "-1"
        self.current_log_typ    = None

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

    ####################################################
    # Log-Datei schreiben / verwalten

    def set_typ( self, log_typ ):
        "Ändert den Log-Typen, der in der DB jedesmal abgespeichert wird"
        self.current_log_typ = log_typ

    def write( self, log_message ):
        "File like writing method"
        self.put( self.current_log_typ, log_message )

    def __call__( self, log_message ):
        # Direkter Call-Aufruf zum schreiben
        self.put( self.current_log_typ, log_message )

    def put( self, log_typ, log_message ):
        "Schreib einen Eintag in die SQL-Log-Tabelle"
        self.check_client_data()

        # Alte Log-Einträge löschen
        self.delete_old_logs()

        SQLcommand  = " INSERT INTO %s" % sql_tablename
        SQLcommand += " ( `timestamp`, `typ`, `sid`, `ip`, `domain`, `message` )"
        SQLcommand += " VALUES (%s, %s, %s, %s, %s, %s);"

        self.db_cursor.execute(
            SQLcommand,
            ( time.time(), log_typ, self.client_sID, self.client_ip, self.client_domain, log_message )
        )

    def delete_old_logs( self ):
        "Löscht veraltete Log-Einträge in der DB"

        SQLcommand  = "DELETE FROM %s" % sql_tablename
        SQLcommand += " WHERE timestamp < %s"

        current_timeout = time.time() - enty_timeout_sec

        self.db_cursor.execute(
            SQLcommand,
            ( current_timeout, )
        )

    ####################################################
    # Log-Datei lesen

    def get_by_IP( self, IP, log_typ=None, plaintext = False ):
        "Alle Log-Einträge von der angegebenen IP-Adresse"

        if log_typ == None:
            SQLcommand  = " SELECT timestamp, typ, sid, ip, domain, message"
            SQLcommand += " FROM %s" % sql_tablename
            SQLcommand += " WHERE ip=%s"
        else:
            SQLcommand  = " SELECT timestamp, sid, ip, domain, message"
            SQLcommand += " FROM %s" % sql_tablename
            SQLcommand += " WHERE ( ip=%s and typ=%s )"

        SQLcommand += " ORDER BY `timestamp` DESC"
        SQLcommand += " LIMIT 0,10"

        if log_typ == None:
            self.db_cursor.execute( SQLcommand, (IP,) )
        else:
            self.db_cursor.execute( SQLcommand, (IP,log_typ) )

        DB_data = self.db_cursor.fetchall()

        if plaintext == False:
            return DB_data

        result = ""
        for line in DB_data:
            timestamp = line[0]
            info = line[1:]
            result += time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(timestamp) )
            result += " - "
            result += ", ".join( [str(i) for i in info] )
            result += "\n"
        return result




