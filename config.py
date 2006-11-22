#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__="0.0.6"

__history__="""
v0.0.6
    - Obsolete: "available_markups" wird unnötig, weil es in der Tabelle
        'markups' steht.
v0.0.5
    - Änderung: Pfade müßen nun nicht mehr per Hand eingetragen werden!
v0.0.4
    - NEU: mod_rewrite_user_agents
    - Änderung: page_ident muß in jedem Fall gesetzt werden
v0.0.3
    - NEU: system.robots_tag
    - NEU: system.ModuleManager_error_handling
    - NEU: system.mod_rewrite_filter
v0.0.2
    - Kleine if-Abfrage nach dbconf ermöglicht das dynamische Modifizieren
        der db-Daten, damit ein lokaler Test einfacher ist.
v0.0.1
    - erste Version
"""

"""configuration

 dbconf
--------
Hier wird von dbcondig.py die DB-Daten eingetragen.
Damit man Lokal, per Remote-SQL-Abfrage das ganze auch benutzen
kann, wird hierbei schon mal die Werte für den SQL-Connect hinterlegt.


 preferences
-------------
Hier werden von preferences.py Einstellungen von
der Tabelle preferences gespeichert.
"""


import os

# request als Objekt, wird hier rein gepflanzt

config = {
    ## Database connection settings
    # sqlite not supported yet!
    "dbTyp"             : "MySQLdb", # "sqlite"

    # Instead of 'localhost' you must possibly use the domain name or IP
    "dbHost"            : 'localhost',
    #~ "dbHost"            : '192.168.6.2',

    "dbDatabaseName"    : 'DatabaseName',
    "dbUserName"        : 'UserName',
    "dbPassword"        : 'Password',
    "dbTablePrefix"     : 'pylucid_', # No blanks may contain!

    # Optional dbapi Arguments
    # example:
    #   If the MySQL socket it not the default (/var/run/mysqld/mysqld.sock).
    #   You can set "unix_socket" to the used sock.
    "dbKeyWordsArgs" : {
        #~ "unix_socket": "/usr/local/pd-admin2/var/mysql.run/mysql.sock",
    },

    # Encoding between SQL-Server and PyLucid
    #   - only supported with MySQL-Server >=v4.1 with <v4.1 sould be 'None'!
    #   - if it 'None', then PyLucid use the Server default encondig
    "db_encoding"       : "utf8",
    #~ "db_encoding"       : None,

    # Only for testing! (MySQL can't use utf_16_be)
    #~ "db_encoding"       : "utf_16_be",

    "dbDatetimeFormat" : '%Y-%m-%d %H:%M:%S', # SQL-Datetime-String-Format

    # Zeigt zusätzlich an, in welchem Modul eine Page-Massage erzeugt wurde
    "page_msg_debug"    : False,
    #~ "page_msg_debug"    : True,

    # Fehlerabfrage bei Module/Plugins über den Module-Manager, sowie bei den
    # Markup Parsern
    # =False -> Fehler in einem Modul führen zu einem CGI-Traceback ( cgitb.enable() )
    # =True  -> Fehler in einem Modul werden in einem Satz zusammen gefasst
    "ModuleManager_error_handling"  : True,
    #~ "ModuleManager_error_handling"  : False,

    # Fehlerabfrage beim importieren von Modulen im Module-Manager
    # =True  -> Import-Fehler werden immer angezeigt
    # =False -> Import-Fehler sehen nur eingeloggte Administratoren
    #~ "ModuleManager_import_error"    : True,
    "ModuleManager_import_error"    : False,

    # Damit Suchmaschienen nicht auch interne Seiten indexieren, passt PyLucid den
    # Inhalt des '<lucidTag:robots/>'-Tag je nach Typ der Seite an.
    # Dazu sollte im Header der Seite eine folgende Zeile stehen:
    # <meta name="robots" content="<lucidTag:robots/>" />
    "robots_tag" : {
        "content_pages"     : "index,follow",
        "internal_pages"    : "noindex"
    },

    # Wird gesetzt sobald es erforderlich ist.
    # Ist die ID der Usergruppe "PyLucid_internal"
    # Damit sind die Internen Seiten in der DB makiert
    # Keine änderung nötig
    "internal_group_id" : -1,

    # Important URL prefix for special sections:
    "installURLprefix" : "_install",
    "commandURLprefix" : "_command",
}







