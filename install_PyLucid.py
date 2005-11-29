#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid "installer"
"""

__version__ = "v0.3.1"

__history__ = """
v0.3.1
    - Packports Pfad hinzugefügt
v0.3
    - Es kann nur einmal ein Admin angelegt werden
    - Benutzt nun einige PyLucid-Objekte (erforderlich für neues userhandling)
    - Möglichkeit dir Markup-String zu IDs zu konvertieren (Änderung in PyLucid v0.5)
    - CSS Spielereien 2
v0.2
    - Anpassung an neue install-Daten-Struktur.
    - "add Admin"-Formular wird mit JavaScript überprüft.
    - NEU Path Check: allerdings wird erstmal nur die Pfade angezeigt, mehr nicht...
    - CSS Spielereien
    - Aussehen geändert
v0.1.0
    - NEU: "partially re-initialisation DB tables" damit kann man nur ausgesuhte
        Tabellen mit den Defaultwerten überschrieben.
v0.0.8
    - Fehler in SQL_dump(): Zeigte SQL-Befehle nur an, anstatt sie auszuführen :(
v0.0.7
    - Neue Art die nötigen Tabellen anzulegen.
v0.0.6
    - Einige anpassungen
v0.0.5
    - NEU: convert_db: Convertiert Daten von PHP-LucidCMS nach PyLucid
v0.0.4
    - Anpassung an neuer Verzeichnisstruktur
v0.0.3
    - NEU: update internal pages
v0.0.2
    - Anpassung an neuer SQL.py Version
    - SQL-connection werden am Ende beendet
v0.0.1
    - erste Version
"""

__todo__ = """
Sicherheitslücke: Es sollte nur ein Admin angelegt werden können, wenn noch keiner existiert!
"""


#~ def testcodec( txt, ascii_test = True, destination="utf_8" ):
    #~ "Testet blind alle Codecs mit encode und decode"
    #~ codecs = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500',
        #~ 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp860',
        #~ 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874',
        #~ 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1140', 'cp1250',
        #~ 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258',
        #~ 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030',
        #~ 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004',
        #~ 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2',
        #~ 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8',
        #~ 'iso8859_9', 'iso8859_10', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'johab',
        #~ 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2',
        #~ 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004',
        #~ 'shift_jisx0213', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8',
        #~ 'idna', 'mbcs', 'palmos',
        #~ 'raw_unicode_escape', 'string_escape',
        #~ 'undefined', 'unicode_escape', 'unicode_internal'
    #~ ]

    #~ codecs += [
        #~ 'rot_13',
        #~ 'base64_codec',
        #~ 'bz2_codec',
        #~ 'hex_codec',
        #~ 'punycode',
        #~ 'quopri_codec',
        #~ 'zlib_codec',
        #~ 'uu_codec'
    #~ ]
    #~ for codec in codecs:
        #~ try:
            #~ print txt.decode( codec ).encode( destination ), " - codec:", codec
        #~ except:
            #~ pass
    #~ print "-"*80

#~ testcodec( "Ein ue...: ü" )
#~ testcodec( "latin-1..: \xfc" )
#~ testcodec( "UTF8.....: \xc3\xbc" )
#~ import sys
#~ sys.exit()


print "Content-type: text/html; charset=utf-8\r\n"


import cgitb;cgitb.enable()
import os, sys, cgi, re, zipfile


if not sys.version.startswith("2.4"):
    # Damit werden erst die "backports" gefunden, wenn Python älter als v2.4 ist
    sys.path.insert( 0, "PyLucid_python_backports" )


import config # PyLucid's "config.py"
from PyLucid_system import SQL
from PyLucid_system import sessiondata
from PyLucid_system import tools
from PyLucid_modules import userhandling

#__________________________________________________________________________



install_zipfile = "PyLucid_SQL_install_data.zip"
dump_filename   = "SQLdata.sql"



#__________________________________________________________________________
## Konvertierungs-Daten (für convert_db)

db_updates = [
    {
        "table"     : "preferences",
        "data"      : {"value":"%d.%m.%Y"},
        "where"     : ("varName","formatDate"),
        "limit"     : 1
    },
    {
        "table"     : "preferences",
        "data"      : {"value":"%H:%M"},
        "where"     : ("varName","formatTime"),
        "limit"     : 1
    },
    {
        "table"     : "preferences",
        "data"      : {"value":"%d.%m.%Y - %H:%M"},
        "where"     : ("varName","formatDateTime"),
        "limit"     : 1
    },
]


#__________________________________________________________________________


print """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>PyLucid Setup</title>
<meta name="robots"             content="noindex,nofollow" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
<style type="text/css">
html, body {
    padding: 30px;
    background-color: #FFFFEE;
}
body {
    font-family: tahoma, arial, sans-serif;
    color: #000000;
    font-size: 0.9em;
    background-color: #FFFFDB;
    margin: 30px;
    border: 3px solid #C9C573;
}
form * {
  vertical-align:middle;
}
input {
    border: 1px solid #C9C573;
    margin: 0.4em;
}
pre {
    background-color: #FFFFFF;
    padding: 1em;
}
#menu li, #menu li a {
    list-style-type: square;
    padding: 0.3em;
}
a {
    color:#00BBEE;
    padding: 0.1em;
}
a:hover {
    color:#000000;
    background-color: #F4F4D2;
}
</style>
<h2>PyLucid Setup %s</h2>""" % __version__
HTML_bottom = "</body></html>"


class SQL_dump:
    """
    Klasse zum "verwalten" des SQL-install-Dumps
    """
    def __init__( self, db ):
        self.db = db

        self.in_create_table = False
        self.in_insert = False

        self.ziparchiv = zipfile.ZipFile( install_zipfile, "r" )

    def import_dump( self ):
        table_names = self.get_table_names()
        print "<pre>"
        for current_table in table_names:
            print "install DB table '%s'..." % current_table,
            command = self.get_table_data(current_table)

            try:
                counter = self.execute_many(command)
            except Exception,e:
                print "ERROR:", e
            else:
                print "OK"

        print "</pre>"

    def _complete_prefix( self, data ):
        return data % { "table_prefix" : config.dbconf["dbTablePrefix"] }

    def install_tables( self, table_names ):
        """ Installiert nur die Tabellen mit angegebenen Namen """
        print "<pre>"
        reinit_tables = list(table_names)
        for current_table in table_names:
            print "re-initialisation DB table '%s':" % current_table
            command = self.get_table_data(current_table)

            print " - Drop table...",
            try:
                status = self.execute(
                    "DROP TABLE `%s%s`;" % (config.dbconf["dbTablePrefix"],current_table)
                )
            except Exception, e:
                print "Error:", e
            else:
                print "OK"

            print " - recreate Table and insert values...",
            try:
                counter = self.execute_many(command)
            except Exception,e:
                print "ERROR:", e
                sys.exit()
            else:
                print "OK"

            reinit_tables.remove(current_table)
            print

        if reinit_tables != []:
            print "Error, Tables remaining:"
            print table_names
        print "</pre>"


    #__________________________________________________________________________________________
    # Zugriff auf ZIP-Datei

    def get_table_data(self, table_name):
        try:
            data = self.ziparchiv.read( table_name+".sql" )
        except Exception, e:
            print "Can't get data for '%s': %s" % (table_name, e)
            sys.exit()

        return self._complete_prefix( data )

    def get_table_names(self):
        """
        Die Tabellen namen sind die Dateinamen, außer info.txt
        """
        table_names = []
        for fileinfo in self.ziparchiv.infolist():
            if fileinfo.filename.endswith("/"):
                # Ist ein Verzeichniss
                continue
            filename = fileinfo.filename
            if filename == "info.txt":
                continue
            filename = os.path.splitext(filename)[0]
            table_names.append(filename)
        table_names.sort()
        return table_names

    #__________________________________________________________________________________________
    # SQL

    def execute_many(self, command):
        """
        In der Install-Data-Datei sind in jeder Zeile ein SQL-Kommando,
        diese werden nach einander ausgeführt
        """
        counter = 0
        for line in command.split("\n"):
            if line=="": # Leere Zeilen überspringen
                continue
            self.execute(line)
            counter += 1
        return counter

    def execute( self, SQLcommand ):
        #~ try:
        self.db.cursor.execute( SQLcommand )
        #~ except Exception, e:
            #~ print "Error: '%s' in SQL-command:" % cgi.escape( str(e) )
            #~ print "'%s'" % SQLcommand
            #~ print
            #~ return False
        #~ else:
            #~ return True

    #__________________________________________________________________________________________

    def dump_data( self ):
        print "<h2>SQL Dump data:</h2>"
        print
        print "<pre>"
        for line in self.data.splitlines():
            print cgi.escape( self._complete_prefix( line )  )
        print "</pre>"










##__________________________________________________________________________________________







class PyLucid_setup:
    def __init__( self ):
        self.PyLucid = {
            "URLs": {},
            "module_manager": None,
        }

        # PyLucid's Konfiguration
        self.config         = config
        self.PyLucid["config"] = self.config

        from index import path
        self.path = path(self.PyLucid)
        self.path.setup()         # setzt die Pfade mit der selben Klasse aus der index.py

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.page_msg       = sessiondata.page_msg()
        self.PyLucid["page_msg"] = self.page_msg

        self.CGIdata = sessiondata.CGIdata( self.PyLucid )
        self.CGIdata["install_PyLucid"] = True
        self.CGIdata["page_id"] = 0
        self.PyLucid["CGIdata"] = self.CGIdata

        tools.PyLucid           = self.PyLucid
        self.PyLucid["tools"]   = tools

        # URLs zusammenbauen, die immer gleich sind.
        self.path.setup_URLs()

        try:
            self.db = SQL.db( self.PyLucid )
        except Exception, e:
            print "<pre>Error:", e
            print "check config in 'config.py' first!</pre>"
            sys.exit()
        self.PyLucid["db"] = self.db

        tools.PyLucid           = self.PyLucid
        self.tools = tools
        self.PyLucid["tools"]   = self.tools

        if self.CGIdata.has_key( "action" ):
            action = self.CGIdata["action"]
            try:
                unbound_method = getattr( self, action ) # Die Methode in dieser Klasse holen
            except AttributeError, e:
                print e
                sys.exit()
            unbound_method() # Methode "starten"
            sys.exit()

        self.actions = [
                (self.install_PyLucid,  "install",              "Install PyLucid from scratch"),
                (self.add_admin,        "add_admin",            "add a admin user"),
                (self.re_init,          "re_init",              "partially re-initialisation DB tables"),
                (self.module_admin,     "module_admin",         "Module/Plugin Administration"),
                (self.convert_markups,  "convert_markups",      "Convert Markup Names to IDs (PyLucid v0.x -&gt; 0.5)"),
                #~ (self.convert_db,       "convert_db",           "convert DB data from PHP-LucidCMS to PyLucid Format"),
                #~ (self.convert_locals,   "locals",               "convert locals (ony preview!)"),
            ]

        for action in self.actions:
            if self.CGIdata.has_key( action[1] ):
                # Ruft die Methode auf, die in self.actions definiert wurde
                action[0]()
                self.end()

        self.print_actionmenu()
        print "<hr>"
        self.print_info()
        self.end()

    def end(self):
        """
        Sollte immer zum Schluß aufgerufen werden!
        """
        self.db.close()
        if self.page_msg.data != "":
            print "<pre>%s</pre>" % self.page_msg.data
        self.print_saftey_info()
        print HTML_bottom
        sys.exit()

    def print_info( self ):
        print "<h4>Path in config.py:</h4>"
        print "<pre>"
        print "script_filename:", config.system.script_filename
        print "document_root:", config.system.document_root
        print "</pre>"
        try:
            print 'Check this link to your PyLucid CMS: <a href="%(url)s">%(url)s</a>' % {"url": config.system.poormans_url}
        except Exception, e:
            print "Error: %s" % e
        print '(If this link is wrong, you <strong>must</strong> change the Path in config.py!!!)'
        print "<hr>"
        print '<p><a href="http://www.pylucid.org">www.pylucid.org</a> |'
        print '<a href="http://www.pylucid.org/index.py?p=/Download/install+PyLucid">install instructions</a> |'
        print '<a href="http://www.pylucid.org/index.py?p=/Download/update+instructions">update instructions</a></p>'

    def print_actionmenu( self ):
        print "Please select:"
        print '<ul id="menu">'
        for i in self.actions :
            print '<li><a href="?%s">%s</a></li>' % (i[1], i[2])

        print "</ul>"

    #__________________________________________________________________________________________

    def install_PyLucid( self ):
        """ Installiert PyLucid von Grund auf """
        print "<h3>Install PyLucid:</h3>"
        self.print_backlink()

        d = SQL_dump( self.db )
        d.import_dump()
        #~ d.dump_data()

    #__________________________________________________________________________________________

    def re_init( self ):
        print "<h3>partially re-initialisation DB tables</h3>"
        self.print_backlink()
        d = SQL_dump( self.db )

        print '<form action="?action=re_init_tables" method="post">'
        print '<p>Which tables reset to defaults:</p>'

        for name in d.get_table_names():
            print '<input type="checkbox" name="table" value="%s">%s<br />' % (name,name)

        print "<h4>WARNING: The specified tables lost all Data!</h4>"
        print '<button type="submit">submit</button>'
        print '</form>'

    def re_init_tables( self ):
        print "<h3>partially re-initialisation DB tables</h3>"
        self.print_backlink()

        d = SQL_dump( self.db )
        try:
            table_names = self.CGIdata['table']
        except KeyError:
            print "<h3>No Tables to reset?!?!</h3>"
            self.print_backlink()
            sys.exit()

        if type(table_names) == str:
            # Nur eine Tabelle wurde ausgewählt
            table_names = [ table_names ]

        d.install_tables( table_names )

        self.print_backlink()

    #__________________________________________________________________________________________

    def module_admin(self):
        self.PyLucid["URLs"]["action"] = "?action=module_admin&sub_action="

        self.print_backlink()

        from PyLucid_modules import module_admin
        module_admin = module_admin.module_admin(self.PyLucid, call_from_install_PyLucid = True)

        sub_action = self.CGIdata.get("sub_action", None)

        if sub_action == "install":
            try:
                module_admin.install(self.CGIdata["package"], self.CGIdata["module_name"])
            except KeyError, e:
                print "KeyError:", e
            return
        elif sub_action == "deinstall":
            try:
                module_admin.deinstall(self.CGIdata["id"])
            except KeyError, e:
                print "KeyError:", e
            return
        elif sub_action == "reinit":
            try:
                module_admin.reinit(self.CGIdata["id"])
            except KeyError, e:
                print "KeyError:", e
            return
        elif sub_action == "activate":
            try:
                module_admin.activate(self.CGIdata["id"])
            except KeyError, e:
                print "KeyError:", e
        elif sub_action == "deactivate":
            try:
                module_admin.deactivate(self.CGIdata["id"])
            except KeyError, e:
                print "KeyError:", e

        module_admin.administation_menu()

        self.print_backlink()

    #__________________________________________________________________________________________

    def convert_markups(self):
        print "<h3>Convert Markup Names to Markup IDs in DB</h3>"
        self.print_backlink()

        try:
            self.db.select(
                select_items    = ["name"],
                from_table      = "markups",
            )
        except Exception,e:
            print "Error:", e
            print "<p><strong>NOTE:</strong> You must first re-init 'markups' table!</p>"
            return

        print "<h4>Convert to numbers:</h4>"
        print "<pre>"

        page_data = self.db.select(
            select_items    = ["id","name","markup"],
            from_table      = "pages",
        )
        for page in page_data:
            markup = self.db.get_markup_id(page["markup"])
            print "%-30s\t%8s -&gt; %s" % (
                cgi.escape(page["name"]),page["markup"], markup
            )
            self.db.update(
                table   = "pages",
                data    = {"markup":markup},
                where   = ("id",page["id"]),
                limit   = 1
            )
        print "</pre>"
        print "<h4>Convert table field</h4>"
        SQLcommand = "ALTER TABLE `$tableprefix$pages` CHANGE `markup` `markup` SMALLINT(1) NULL DEFAULT '1';"
        print "<pre>"
        print SQLcommand
        try:
            status = self.db.get( SQLcommand )
        except Exception, e:
            print "Error: %s" % e
        else:
            if status == ():
                print "OK"
            else:
                print "Error:", status
        print "</pre>"
        self.print_backlink()

    #__________________________________________________________________________________________

    def setup_db( self ):
        print "<pre>"
        for SQLcommand in SQL_table_data.split("----"):
            SQLcommand = SQLcommand.strip() % {
                "dbTablePrefix" : config.dbconf["dbTablePrefix"]
            }
            SQLcommand = SQLcommand.replace("\n"," ")
            table_name = re.findall( "TABLE(.*?)\(", SQLcommand )[0]
            comment = re.findall( "COMMENT.*?'(.*?)'", SQLcommand )[0]

            print "Create table '%s' (%s) in DB" % (table_name,comment)
            #~ print SQLcommand
            self.execute( SQLcommand )
            print
        print "</pre>"

    #__________________________________________________________________________________________

    def base_content( self ):
        print "<pre>"
        old_table_name = ""
        for SQLcommand in base_content.split("INSERT"):
            SQLcommand = SQLcommand.strip()
            if SQLcommand == "":
                continue

            SQLcommand = "INSERT " + SQLcommand

            # Mit einem String-Formatter kann man leider nicht arbeiten, weil
            # In den Inhalten mehr Platzhalter vorkommen können!
            SQLcommand = SQLcommand.replace( "%(dbTablePrefix)s", config.dbconf["dbTablePrefix"] )

            #~ print cgi.escape( SQLcommand ).encode( "String_Escape" )

            table_name = re.findall( "INTO `(.*?)` VALUES", SQLcommand )[0]
            if table_name != old_table_name:
                print "put base content into table:", table_name
                old_table_name = table_name

            self.execute( SQLcommand )
        print "</pre>"

    #__________________________________________________________________________________________

    def add_admin( self ):
        """ Einen neuen Admin anlegen """
        print "<h3>Add Admin:</h3>"
        self.print_backlink()

        if self.db.exists_admin() == True:
            print "<h3>Sorry, an admin already exists.</h3>"
            print "<p>For safety reasons: Only one User can create here.<br />"
            print "Log in and create new Users!</p>"
            self.end()

        if not self._has_all_keys( self.CGIdata, ["username","email","pass1"] ):
            self.db.print_internal_page("add_user_form", {"url":"?add_admin"})
            print "<strong>Note:</strong> Is admin checkbox ignored. Always create a admin account!"
            return

        if not self.CGIdata.has_key("realname"):
            self.CGIdata["realname"] = None

        usermanager = userhandling.userhandling( self.PyLucid )
        try:
            usermanager.add_user(
                username    = self.CGIdata["username"],
                email       = self.CGIdata["email"],
                realname    = self.CGIdata["realname"],
                admin       = 1
            )
        except KeyError, e:
            print "CGIdata KeyError: '%s' not found! No user is added!" % e


    ###########################################################################################

    def convert_db( self ):
        print "<h3>convert PHP-LucidCMS data to PyLucid Format</h3>"
        print "<pre>"

        for item_data in db_updates:
            print item_data
            self.db.update(
                table   = item_data["table"],
                data    = item_data["data"],
                where   = item_data["where"],
                limit   = item_data["limit"],
            )

        print "</pre>"
        print "<h4>OK</h4>"
        print '<a href="?">back</a>'


    #__________________________________________________________________________________________

    def default_internals( self ):
        print "<h3>set all internal pages to default.</h3>"
        self.print_backlink()
        print "<pre>"

        self.make_default_internals()

        print "</pre>"
        self.print_backlink()

    def make_default_internals( self ):
        for page in internal_pages:
            print "update page '%s' in table 'pages_internal'" % page["name"]
            try:
                self.db.update(
                    table   = "pages_internal",
                    data    = page,
                    where   = ("name",page["name"]),
                    limit   = 1
                )
            except Exception, e:
                print "Error: '%s'" % e
            print

    #__________________________________________________________________________________________


    def convert_locals( self ):
        print '<p><a href="?">back</a></p>'
        print "<h3>Convert locals</h3>"
        print "<p>converts the encoding of all page-data in the SQL-DB</p>"

        if not self._has_all_keys( self.CGIdata, ["source_local","destination_local"] ):
            print '<form name="locals" method="post" action="?locals">'
            print '<p>'
            print 'source encoding: <input name="source_local" type="text" value="latin-1"><br />'
            print 'destination encoding: <input name="destination_local" type="text" value="UTF8"><br />'
            print 'convert:<br/>'
            print '<input name="name_title" type="checkbox" id="name_tile" value="1" /> side name/title<br/>'
            print '<input name="content" type="checkbox" id="content" value="1" checked="checked" /> side content<br/>'
            print "</p><p>"
            print 'Preview only: <input name="preview" type="checkbox" id="preview" value="1" checked="checked" /><br />'
            print '<input type="submit" name="Submit" value="convert" />'
            print '</p></form>'
            sys.exit()

        if not (self.CGIdata.has_key("name_title") or self.CGIdata.has_key("content")):
            print "Ups, nothing to do!"
            sys.exit()

        source_local        = self.CGIdata["source_local"]
        destination_local   = self.CGIdata["destination_local"]

        side_data = self.db.select(
                select_items    = ["id","name", "title", "content"],
                from_table      = "pages",
            )

        if self.CGIdata.has_key("preview"):
            print "<h3>Preview:</h3>"

        def dec( txt ):
            return txt.decode( source_local ).encode( destination_local )

        for side in side_data:
            name    = dec( side["name"] )
            title   = dec( side["title"] )
            content = dec( side["content"] )
            if self.CGIdata.has_key("preview"):
                if self.CGIdata.has_key("name_title"):
                    print "side name '%s' - side title '%s'<br/>" %  (name, title)

                if self.CGIdata.has_key("content"):
                    if content == side["content"]:
                        print "[Encoding is the same!]"
                    else:
                        print "content: %s [...]" % cgi.escape( content[:150] )
                print "<hr>"
                continue

            #~ testcodec( side["name"] )
            #~ print "-"*80
            #~ daten = side["name"].encode("string_escape")
            #~ testcodec( daten )
            #~ print side["name"].decode( source_local )
            #~ print side["name"].encode( destination_local )

    ###########################################################################################
    ###########################################################################################

    def execute( self, SQLcommand ):
        try:
            self.db.cursor.execute( SQLcommand )
        except Exception, e:
            print "Error: '%s'" % e


    def _has_all_keys( self, dict, keys ):
        for key in keys:
            if not dict.has_key( key ):
                return False
        return True

    def print_backlink( self, section = "" ):
        print '<p><a href="?%s">back</a></p>' % section

    def print_saftey_info( self ):
        print "<hr>"
        print "<h3>For safety reasons:</h3>"
        print "<h4>After setup: Delete this file (%s) on the server !!!</h4>" % os.environ["SCRIPT_NAME"]


if __name__ == "__main__":
    #~ print "<pre>"
    PyLucid_setup()



