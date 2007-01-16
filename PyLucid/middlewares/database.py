#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Database - Middelware


Aufbau, durch erben der Klassen:

 5. db.db()

 4. SQL_active_statements.active_statements()
     ^-Alle SQL Sachen die Daten verändern, erbt von SQL_passive_statements.py

 3. SQL_passive_statements.passive_statements()
     ^-Alle "nur select" Befehle, erbt von SQL_wrapper.py

 2. DBwrapper.SQL_wrapper()
     ^-Wrapper für die SQL-Befehle

 1. DBwrapper.Database()
     ^-Stellt die DB Verbindung her, bietet Dict-Cursor und Conn.Objekt

d.h.:
    active_statements erbt von passive_statements
    passive_statements erbt vom SQL_wrapper
    SQL_wrapper erbt von Database



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

__version__= "$Rev$"


from PyLucid.system.SQL_active_statements import active_statements
from PyLucid.system.DBwrapper.DBwrapper import ConnectionError

class db(active_statements):
    def connect(self, preferences):

        self.tableprefix    = preferences["dbTablePrefix"]
        self.db_date_format = preferences["dbDatetimeFormat"]

        self.connect_mysqldb(
            host    = preferences["dbHost"],
            user    = preferences["dbUserName"],
            passwd  = preferences["dbPassword"],
            db      = preferences["dbDatabaseName"],
            **preferences["dbKeyWordsArgs"]
        )



class DatabaseMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        self.environ = environ

        page_msg    = environ['PyLucid.page_msg']
        preferences = environ['PyLucid.config']

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.dbObj = db(page_msg)

        environ['PyLucid.database'] = self.dbObj

        return self.app(environ, start_response)





