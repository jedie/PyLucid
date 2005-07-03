
PyLucid v0.2.0
==============

copyleft 2005 by Jens Diemer
Wie all meine Programme, stehen auch dieses unter der GPL-Lizenz.

Aktuelle Version auf meiner Homepage: http://www.jensdiemer.de


!!! Diese Doku muß noch aktualisiert werden !!!


Was ist PyLucid ?

PyLucid entwickelt sich langsam zum eigenständigen CMS in pure Python CGI! Es benötigt keine zusätzlichen Module (außer der SQL anbindung über mySQLdb ) und ist ab Python v2.2.1 lauffähig (evtl. auch mit noch älteren Versionen). mySQLdb ist allerdings i.d.R. bei jedem WebHoster vorinstalliert.
Da die Datenbankarchitektur in der Basis gleich zum PHP LucidCMS ist, kann man beide systeme parallel betreiben. Das heißt, man kann die komplette Administration aus beiden Systemen gleichzeitig nutzen.

Nun wird meine Homepage komplett mit PyLucid gerendert. Dazu kommt TinyTextile zum einsatz.


Welche Module gibt es?

 <lucidTag:back_links/> - BackLinks.py
 -------------------------------------
 Generiert eine horizontale zurück-Linkleiste

    !!!Obsolet!!! Einzubinden über lucid-IncludeRemote-Tag:
    <lucidFunction:IncludeRemote>http://localhost/cgi-bin/PyLucid/BackLinks.py?page_name=<lucidTag:page_name/></lucidFunction>



 <lucidTag:main_menu/> - Menu.py
 -------------------------------
 Generiert das komplette Hauptmenü mit Untermenüs

    !!!Obsolet!!! eingebunden kann es per lucid-"IncludeRemote"-Tag:
    <lucidFunction:IncludeRemote>http://localhost/cgi-bin/PyLucid/Menu.py?page_name=<lucidTag:page_name/></lucidFunction>



 ListOfNewSides.py
 -----------------
 Generiert eine Liste der Seiten die zuletzt geändert worden sind



Wie benutzen ?

 !!!Obsolet!!!

 1. Unter "./system/config.py" muß der Pfad zur Konfigurations-Datei
    von Lucid angegeben werden.
 2. Das ganze auf dem WebSpace z.B. unter "/cgi-bin/PyLucid/" packen.
 3. Zum einbinden in einer CMS-Seite den "IncludeRemote"-Tag benutzen.
    z.B.: <lucidFunction:IncludeRemote>http://localhost/cgi-bin/PyLucid/ListOfNewSides.py</lucidFunction>
    ( http://localhost muß evtl. durch den Domainnamen ersetzt werden! )

 Zum lokalen Testen muß in der "./system/config.py" die SQL-Konfig bei dict dbconf
 eingetragen werden. Diese werden dann nicht überschrieben, sondern genutzt.


 History
=========
v0.0.4
    - Großer Umbau, da das rendern der Seiten nun von PyLucid, also den Python CGI's, übernommen wird
v0.0.3
    - Menu: Menulink mit 'title' erweitert, Link-Text ist nun 'name'
v0.0.2
    - neue Module: Menu, Search, BackLinks
    - ListOfNewSides: Nur Seiten Anzeigen, die auch permitViewPublic=1 sind (also Ã¶ffentlich)
v0.0.1
    - erste Version