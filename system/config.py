#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__="0.0.2"

__history__="""
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


class system:
    # Pfad zur Konfigurations-Datei
    # Absolut zum DocRoot-Verz.
    #~ PHPdbconfig = "dbConfig.php"

    # Pfad zur Ralf Mieke's md5.js
    # http://www.miekenet.de
    # http://aktuell.de.selfhtml.org/artikel/javascript/md5/
    md5javascript = "/PyLucid/md5.js"

    # Pfad zur PyLucid md5manager.js Datei
    # Wird für den Login benötigt!!!
    md5manager = "/PyLucid/md5manager.js"

    # Wird gesetzt sobald es erforderlich ist.
    # Ist die ID der Usergruppe "PyLucid_internal"
    # Damit sind die Internen Seiten in der DB makiert
    internal_group_id = -1

    # Die Adresse zur PyLucid index Datei, der Pfad
    # muß absolut gesetzt werden!
    real_self_url = "/cgi-bin/PyLucid/index.py"

    # Wenn eine schöne Adresse generiert werden soll
    # und kein apache mod-rewrite zur verfügung steht,
    # aber SSI, dann kann man sich damit eine schönere
    # URL bauen:
    # <!--#exec cgi="/cgi-bin/PyLucid/index.py" -->
    poormans_url = "/"



dbconf = {
    "dbHost"            : 'localhost',
    "dbDatabaseName"    : 'DatabaseName',
    "dbUserName"        : 'UserName',
    "dbPassword"        : 'Password',
    "dbTablePrefix"     : 'lucid_'
}

preferences = {
    # Für render.py, damit bei specialTags (z.B. <lucidFunction:IncludeRemote>) angegebenes Skripte
    # z.B. ListOfNewSides.py nicht wirklich per http gehohlt werden, sondern als Python-Module direkt
    # ausgeführt werden.
    "LocalDomain" : ( "http://localhost", "http://jensdiemer.de", "http://www.jensdiemer.de" )

    # "internal_group_id" - dieser Key wird gesetzt, wenn der User
    }

class readpreferences:
    """
    lucid-preferences aus Datenbank lesen und im preferences-Dict eintragen
    """

    def __init__( self, db ):
        self.db = db
        #~ print "Content-type: text/html\n\n<pre>"
        # Daten aus DB lesen
        pref_data = self.db.get_preferences()

        # Daten eintragen
        self.put_to_config( pref_data )

    def put_to_config( self, pref_data ):
        for item in pref_data:
            #~ {'varName': 'defaultPageName', 'section': 'core', 'value': '1'}
            #~ print i
            if not preferences.has_key( item["section"] ):
                preferences[ item["section"] ] = {}

            preferences[ item["section"] ][ item["varName"] ] = item["value"]




class search:
    # Relativ zum PyLicid-Verzeichnis
    indexDBfile = "files/SearchIndex.bin"

LogDatei = "log/%s.log"




