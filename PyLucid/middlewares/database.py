#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Middelware

Database
"""


#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

"""
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
"""

__version__="0.5"

__history__="""
v0.5
    - Neu: dbKeyWordsArgs
v0.4
    - nochmal umgebaut. DBwrapper ist nun per SVN-external eingebunden
v0.3
    - Aufteilung in database, Wrapper, passive- und active-Statements
    - History hierhin verschoben
v0.2.2
    - Umstellung bei Internen Seiten: Markup/Template
v0.2.1
    - Bessere Fehlerbehandlung beim Zugriff auf die Internen seiten.
v0.2
    - NEU: get_last_logs()
    - Bug in delete_style
v0.1
    - NEU: new_internal_page()
v0.0.11
    - Bug in get_internal_page() bei Fehlerabfrage.
v0.0.10
    - In get_side_data() wird bei keywords und description beim Wert None automatisch ein ="" gemacht
v0.0.9
    - NEU: print_internal_page() Sollte ab jetzt immer direkt genutzt werden, wenn eine interne Seite
        zum einsatzt kommt. Damit zentral String-Operating Fehler abgefangen werden.
v0.0.8
    - Nun können auch page_msg abgesetzt werden. Somit kann man hier mehr Inteligenz bei Fehlern einbauen
    - Neue Fehlerausgabe bei get_internal_page() besser im zusammenhang mit dem Modul-Manager
    - Neu: userdata()
    - Neu: get_available_markups()
v0.0.7
    - order=("name","ASC") bei internal_page-, style- und template-Liste eingefügt
    - get_page_link_by_id() funktioniert auch mit Sonderzeichen im Link
v0.0.6
    - Fehlerausgabe geändert
    - Fehlerausgabe bei side_template_by_id() wenn Template nicht existiert.
v0.0.5
    - NEU: Funktionen für das editieren von Styles/Templates
v0.0.4
    - SQL-wrapper ausgelagert in mySQL.py
v0.0.3
    - Allgemeine SQL insert und update Funktion eingefügt
    - SQL-where-Parameter kann nun auch meherere Bedingungen haben
v0.0.2
    - Allgemeine select-SQL-Anweisung
    - Fehlerausgabe bei fehlerhaften SQL-Anfrage
v0.0.1
    - erste Release
"""


from PyLucid.system.SQL_active_statements import active_statements
from PyLucid.system.DBwrapper.DBwrapper import ConnectionError

class db(active_statements):
    def connect(self, preferences):

        self.tableprefix    = preferences["dbTablePrefix"]
        self.datetimefix    = preferences["dbDatetimeFix"]
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

        db_encoding = preferences["db_encoding"]

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.dbObj = db(page_msg, db_encoding)

        environ['PyLucid.database'] = self.dbObj

        return self.app(environ, start_response)





