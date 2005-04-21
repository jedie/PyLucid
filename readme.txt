
PyLucid v0.0.1
==============

copyleft 2005 by Jens Diemer
Wie all meine Programme, stehen auch dieses unter der GPL-Lizenz.


Was ist PyLucid ?

    Python-CGI Erweiterungen für das LucidCMS: http://lucidcms.net/


Welche Erweiterungen ?

 ListOfNewSides.py
 -----------------
 Generiert eine Liste der Seiten die zuletzt geändert worden sind


Wie benutzen ?

 1. Unter "./system/config.py" muß der Pfad zur Konfigurations-Datei
    von Lucid angegeben werden.
 2. Das ganze auf dem WebSpace z.B. unter "/cgi-bin/PyLucid/" packen.
 3. Zum einbinden in einer CMS-Seite den "IncludeRemote"-Tag benutzen.
    z.B.:
    <lucidFunction:IncludeRemote>/cgi-bin/PyLucid/ListOfNewSides.py</lucidFunction>

 Zum lokalen Testen muß in der "./system/config.py" die SQL-Konfig bei dict dbconf
 eingetragen werden. Diese werden dann nicht überschrieben, sondern genutzt.