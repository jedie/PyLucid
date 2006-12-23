#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid Grundeinstellungen für den Zugriff auf die Datenbank



Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author: jensdiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev:$"




config = {
    ## Database connection settings
    "dbTyp"             : "MySQLdb", # Only MySQL supported yet!

    # Instead of 'localhost' you must possibly use the domain name or IP
    "dbHost"            : 'localhost',

    "dbDatabaseName"    : 'DatabaseName',
    "dbUserName"        : 'UserName',
    "dbPassword"        : 'Password',

    "dbTablePrefix"     : 'pylucid_', # No blanks may contain!

    ## Optional dbapi Arguments
    # example:
    #   If the MySQL socket it not the default (/var/run/mysqld/mysqld.sock).
    #   You can set "unix_socket" to the used sock.
    "dbKeyWordsArgs" : {
        #~ "unix_socket": "/usr/local/pd-admin2/var/mysql.run/mysql.sock",
    },

    "dbDatetimeFormat" : '%Y-%m-%d %H:%M:%S', # SQL-Datetime-String-Format

    # Zeigt zusätzlich an, in welchem Modul eine Page-Massage erzeugt wurde
    "page_msg_debug"    : False,
    #~ "page_msg_debug"    : True,

    # Fehlerabfrage bei Module/Plugins über den Module-Manager, sowie bei den
    # Markup Parsern
    # =False -> Fehler in einem Modul führen zu einem CGI-Traceback
    # =True  -> Fehler in einem Modul werden in einem Satz zusammen gefasst
    "ModuleManager_error_handling"  : True,
    #~ "ModuleManager_error_handling"  : False,

    # Fehlerabfrage beim importieren von Modulen im Module-Manager
    # =True  -> Import-Fehler werden immer angezeigt
    # =False -> Import-Fehler sehen nur eingeloggte Administratoren
    #~ "ModuleManager_import_error"    : True,
    "ModuleManager_import_error"    : False,

    ## ATM unused but maybe usefull in feature --> see handler.py for more information
    # At this point you can define how to use PyLucid.
    # you can choose between "mod_python", "fcgi" and "cgi"
    # btw... a standalone-handler???
    # more should be added... ;)
    "environment"    : "cgi",

    #_________________________________________________________________________
    ## Die folgenden Einstellungen müßen i.d.R. nicht geändert werden!

    # Damit Suchmaschienen nicht auch interne Seiten indexieren, passt PyLucid
    # den Inhalt des '<lucidTag:robots/>'-Tag je nach Typ der Seite an.
    # Dazu sollte im Header der Seite eine folgende Zeile stehen:
    # <meta name="robots" content="<lucidTag:robots/>" />
    "robots_tag" : {
        "content_pages"     : "index,follow",
        "internal_pages"    : "noindex"
    },

    # Wird gesetzt sobald es erforderlich ist.
    # Ist die ID der Usergruppe "PyLucid_internal"
    # Damit sind die Internen Seiten in der DB makiert
    # Keine Änderung nötig
    "internal_group_id" : -1,

    # Important URL prefix for special sections:
    "installURLprefix" : "_install",
    "commandURLprefix" : "_command",
}







