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
    md5javascript = "/PyLucid_JS/md5.js"

    # Pfad zur PyLucid md5manager.js Datei
    # Wird für den Login benötigt!!!
    md5manager = "/PyLucid_JS/md5manager.js"

    # Wird gesetzt sobald es erforderlich ist.
    # Ist die ID der Usergruppe "PyLucid_internal"
    # Damit sind die Internen Seiten in der DB makiert
    internal_group_id = -1

    ## real_self_url und poormans_url
    # Bei manchen Webhostern sind CGI Programm nicht außerhalb
    # des ./cgi-bin Verzeichnisses erlaubt :( Es ist sehr
    # unwahrscheinlich das man dann aber Apache's mod_rewrite
    # zur Verfügung hat.
    # Um dennoch eine halbwegs "saubere" URL zu haben, hab ich mir
    # da was ausgedacht. Mit Hilfe von SSI (Server Side Include)
    # ist es möglich eine halbwegs schöne URL zu backen.
    #
    # Im Hauptverzeichnis seines WebSpace packt man eine Indexdatei
    # mit folgendem Inhalt:
    #
    # ./index.shtml
    # ------------------------------------------------------
    # <!--#exec cgi="/cgi-bin/PyLucid/index.py" -->
    # ------------------------------------------------------
    #
    # Leider werden keine POST und GET Informationen mit so einer
    # SSI-Ausführung an PyLucid weiter geleitet. Deshalb muß die
    # real_self_url Variable auf die echte index.py weisen.
    # Der Pfad muß absolut gesetzt werden!
    #
    # Zur generierung der schönen URL, also für alle normalen
    # Seitenaufrufe dient die poormans_url Variable.
    #
    # Beispiel Konfiguration
    # ----------------------
    #   - nur /cgi-bin/ erlaubt
    #   - SSI verfügbar: /index.shtml eingerichtet
    # real_self_url = "/cgi-bin/PyLucid/index.py"
    # poormans_url = "/"
    #
    #   - CGIs auch außerhalb von /cgi-bin/ erlaubt
    #   - /index.python
    # real_self_url = "/"
    # poormans_url = "/"
    #
    real_self_url   = "/"
    poormans_url    = "/"



dbconf = {
    "dbHost"            : 'localhost', # Evtl. muß hier die Domain rein
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



def debug():
    import cgi

    print "Content-type: text/html\n"
    print "<h1>config-Debug:</h1>"
    print system
    print "<hr>"
    print "<h3>config.preferences:</h3>"
    print "<pre>"
    #~ print preferences
    for k,v in preferences.iteritems():
        print k,"-",cgi.escape( str(v) )
    print "</pre>"


