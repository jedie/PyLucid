#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__="0.0.3"

__history__="""
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


class system:
    # Zeigt zusätzlich an, in welchem Modul eine Page-Massage erzeugt wurde
    page_msg_debug = False
    #~ page_msg_debug = True

    # Fehlerabfrage bei Module/Plugins über den Module-Manager
    # =False -> Fehler in einem Modul führen zu einem CGI-Traceback ( cgitb.enable() )
    # =True  -> Fehler in einem Modul werden in einem Satz zusammen gefasst
    ModuleManager_error_handling = True

    # Fehlerabfrage beim importieren von Modulen im Module-Manager
    # =True  -> Import-Fehler werden immer angezeigt
    # =False -> Import-Fehler sehen nur eingeloggte Administratoren
    ModuleManager_import_error = False

    # Damit Suchmaschienen nicht auch interne Seiten indexieren, passt PyLucid den
    # Inhalt des '<lucidTag:robots/>'-Tag je nach Typ der Seite an.
    # Dazu sollte im Header der Seite eine folgende Zeile stehen:
    # <meta name="robots" content="<lucidTag:robots/>" />
    robots_tag = {
        "content_pages"     : "index",  # Alle Seiten die ein ?command=xyz haben
        "internal_pages"    : "noindex" # Normale CMS-Seiten
    }

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
    # Das klappt allerdings nur, wenn Apache als Index ein Python
    # Skript benutzen würde.
    # http://httpd.apache.org/docs/2.0/mod/mod_dir.html#directoryindex
    # DirectoryIndex index.py
    #
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
    # real_self_url = "/index.py"
    # poormans_url = "/"
    #
    real_self_url   = "/index.py"
    poormans_url    = "/"
    #
    # Mit welchem Parameter sollen die Links gebildet werden
    # Standart: "?p="
    page_ident      = "?p="

    ## poormans_modrewrite
    # Um auch ohne apache's Modrewrite eine saubere URL *ohne* URL-Parameter
    # zu erhalten kann man mittels "Customized error messages" in der
    # .htaccess arbeiten. Dabei legt man für einen 404 Fehler (Seite nicht
    # gefunden) das ErrorDocument auf die PyLucid's index.py Seite fest.
    # Bsp .htaccess Eintrag:
    # ErrorDocument 404 /index.py
    #
    # Ausgewertet wird dabei der os.environ-Eintrag "REQUEST_URI"
    # Mit poormans_modrewrite muß page_ident="" sein!
    #~ poormans_modrewrite = True
    poormans_modrewrite = False
    #
    # Für eine schnellere Abarbeitung echter "404 Not Found" Fehler
    # beim "poormans_modrewrite = True" werden Requests auf Dateien
    # mit den angegebenen Endungen direkt am Anfang abgehandelt.
    mod_rewrite_filter = ("py","php","js","css","gif","png","jpg","jpeg")


## Hinweis
# der Tabellen-Prefix sollte keine Leer-/Sonderzeichen erhalten.
dbconf = {
    "dbHost"            : 'localhost', # Evtl. muß hier die Domain rein
    "dbDatabaseName"    : 'DatabaseName',
    "dbUserName"        : 'UserName',
    "dbPassword"        : 'Password',
    "dbTablePrefix"     : 'lucid_',
    "dbdatetime_format" : '%Y-%m-%d %H:%M:%S', # SQL-Datetime-String-Format
}


available_markups = ["none","textile"]



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


