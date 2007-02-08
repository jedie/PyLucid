#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Logging in SQL

Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

import time, datetime, os

# Legt fest wie alt Log-Einträge max sein dürfen
# 3 Tage ==> 3Tage * 24Std * 60Min * 60Sec = 259200sec
enty_timeout_sec = 259200

sql_tablename = "log"


class log(object):
    """
    PyLucid SQL-Logging Klasse
    """
    def __init__ (self):
        """
        Default-Werte setzten
        Nachdem eine Session erstellt wurde, werden diese Werte von index.py
        gesetzt
        """
        self.client_sID         = "unknown"
        self.client_user_name   = "unknown"
        self.client_ip          = "unknown"
        self.client_domain_name = "unknown"

    def init2(self, request, response):
        # shorthands
        self.request    = request
        self.db         = request.db
        self.tools      = request.tools
        self.page_msg   = response.page_msg

        self.client_ip = request.environ.get("REMOTE_ADDR","unknown")


    def check_type(self, type):
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

    #_________________________________________________________________________
    ## Log-Datei schreiben / verwalten

    def write(self, log_message, type=False, status="-1"):
        "File like writing method"
        self.put( log_message, type, status )

    def __call__(self, log_message, type=False, status="-1"):
        # Direkter Call-Aufruf zum schreiben
        self.put( log_message, type, status )

    def put(self, log_message, type=False, status="-1"):
        "Schreib einen Eintag in die SQL-Log-Tabelle"

        type = self.check_type( type )

        # Alte Log-Einträge löschen
        self.delete_old_logs()

        timestamp = datetime.datetime.now()

        try:
            self.db.insert(
                table = "log", # Prefix wird bei db.insert eingefügt
                data  = {
                    "timestamp" : timestamp,
                    "sid"       : self.client_sID,
                    "user_name" : self.client_user_name,
                    "ip"        : self.client_ip,
                    "domain"    : self.client_domain_name,
                    "message"   : log_message,
                    "typ"       : type,
                    "status"    : status,
                }
            )
        except Exception, e:
            self.page_msg.red("Can't write to SQL log table: %s" % e)
            try:
                self.db.rollback()
            except Exception, e:
                self.page_msg.red("Can't make DB rollback: %s" % e)
            else:
                self.page_msg.green("make db rollback, OK")
        else:
            self.db.commit()

    def delete_old_logs(self):
        "Löscht veraltete Log-Einträge in der DB"

        SQLcommand  = "DELETE FROM $$%s" % sql_tablename
        SQLcommand += " WHERE timestamp < %s"

        now = datetime.datetime.now()
        current_timeout = now - datetime.timedelta(seconds=enty_timeout_sec)

        try:
            self.db.cursor.execute(SQLcommand, (current_timeout,))
        except Exception, e:
            self.page_msg.red("Can't delete old logs: %s" % e)
            try:
                self.db.rollback()
            except Exception, e:
                self.page_msg.red("Can't make DB rollback: %s" % e)
            else:
                self.page_msg.green("make db rollback, OK")
        else:
            self.db.commit()

    #_________________________________________________________________________
    ## Log-Datei lesen

    def items(self):
        """
        Generiert eine Liste der letzten 5 Logeinträge für die Debug Anzeige
        """
        #~ self.page_msg("lastLog: %s" % self.get_last_logs())

        try:
            last_logs = self.get_last_logs(limit=5)
        except AttributeError:
            # Wenn noch kein init2 ausgeführt wurde, existiert noch kein
            # self.db Objekt!
            return []

        result = []
        for item in last_logs:
            line = "User: %s - ID: %s - typ: %s - msg: %s" % (
                item["user_name"], item["sid"], item["typ"], item["message"]
            )
            result.append((str(item["timestamp"]), line))
        return result


    def get_last_logs( self, limit=10 ):
        """ Liefert die letzten >limit< Logeinträge zurück """
        try:
            return self.db.select(
                select_items    = [
                    "timestamp", "sid", "user_name", "ip", "domain",
                    "message", "typ", "status"
                ],
                from_table      = sql_tablename,
                order           = ("id","DESC"),
                limit           = (0,limit)
            )
        except Exception, e:
            return []

    def debug_last(self):
        import inspect
        self.page_msg(
            "Log Debug (from '%s' line %s):" % (
                inspect.stack()[1][1][-20:], inspect.stack()[1][2]
            )
        )
        for item in self.get_last_logs(limit=10):
            self.page_msg(item["timestamp"], item["sid"], item["message"])



