#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""PyLucid "installer"

Evtl. muß der Pfad in dem sich PyLucid's "config.py" sich befindet
per Hand angepasst werden!
"""

__version__ = "v0.0.8"

__history__ = """
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





import cgitb;cgitb.enable()
import os, sys, cgi, re, zipfile



# Interne PyLucid-Module einbinden
# Verzeichnis in dem PyLucid's "config.py" sich befindet, in den Pfad aufnehmen
#~ sys.path.insert( 0, os.environ["DOCUMENT_ROOT"] )
#~ sys.path.insert( 0, os.environ["DOCUMENT_ROOT"] + "cgi-bin/PyLucid" )

import config # PyLucid's "config.py"
from PyLucid_system import SQL, sessiondata, userhandling

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


HTML_head = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>PyLucid Setup</title>
<meta name="robots"             content="noindex,nofollow" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
<h2>PyLucid Setup %s</h2>""" % __version__


class SQL_dump:

    re_create_table = re.compile( r"(?ims)(CREATE TABLE.*?;)" )
    re_insert_value = re.compile( r"(?ims)(INSERT INTO.*?;)\n" )

    def __init__( self, db ):
        self.db = db

        self.in_create_table = False
        self.in_insert = False

        self.data = self._get_zip_dump()

    def _get_zip_dump( self ):
        print "Open '%s'..." % install_zipfile,
        ziparchiv = zipfile.ZipFile( install_zipfile, "r" )
        data = ziparchiv.read( dump_filename )
        ziparchiv.close()
        print "OK"

        return data

    def execute_SQL_list( self, command_list ):
        count = 0
        for command in command_list:
            status = self.execute( command )
            if status == True:
                count += 1
        return count

    def import_dump( self ):
        print "<pre>"
        create_tables = self.re_create_table.findall( self.data )
        create_tables = [self._complete_prefix(i) for i in create_tables]
        count = self.execute_SQL_list( create_tables )
        print count, "Tables created."
        print

        insert_values = self.re_insert_value.findall( self.data )
        insert_values = [self._complete_prefix(i) for i in insert_values]
        count = self.execute_SQL_list( insert_values )
        print count, "items insert."

    def _complete_prefix( self, line ):
        return line % { "table_prefix" : config.dbconf["dbTablePrefix"] }

    def dump_data( self ):
        print "<h2>SQL Dump data:</h2>"
        print
        print "<pre>"
        for line in self.data.splitlines():
            print cgi.escape( self._complete_prefix( line )  )
        print "</pre>"

    def execute( self, SQLcommand ):
        try:
            self.db.cursor.execute( SQLcommand )
        except Exception, e:
            print "Error: '%s'" % cgi.escape( str(e) )
            return False
        else:
            return True


class PyLucid_setup:
    def __init__( self ):
        print HTML_head
        try:
            self.db = SQL.db()
        except:
            print "check config in 'config.py' first!"
            sys.exit()


        self.CGIdata = sessiondata.CGIdata( {"page_msg":""} )

        #~ print "<p>CGI-data debug: '%s'</p>" % self.CGIdata

        self.actions = [
                (self.install_PyLucid,  "install",              "Install PyLucid from scratch"),
                (self.add_admin,        "add_admin",            "add a admin user"),
                (self.default_internals,"default_internals",    "set all internal pages to default"),
                (self.convert_db,       "convert_db",           "convert DB data from PHP-LucidCMS to PyLucid Format"),
                #~ (self.sql_dump,         "sql_dump",             "SQL dump (experimental)"),
                #~ (self.convert_locals,   "locals",               "convert locals (ony preview!)"),
            ]

        for action in self.actions:
            if self.CGIdata.has_key( action[1] ):
                # Ruft die Methode auf, die in self.actions definiert wurde
                action[0]()
                sys.exit()

        self.print_actionmenu()
        self.check_system()

        self.db.close()

    def check_system( self ):
        def check_file_exists( filepath, txt ):
            filepath = os.path.normpath( os.environ["DOCUMENT_ROOT"] + "/" + filepath )
            if not os.path.isfile( filepath ):
                print "Error:"
                print txt
                print "Please check settings in 'PyLucid/system/config.py' !!!"
            else:
                print txt,"file found - OK"

        print "<hr><pre>"
        print "System check:"
        print

        check_file_exists( config.system.md5javascript, "Ralf Mieke's 'md5.js'-File" )
        check_file_exists( config.system.md5manager, "PyLucid's 'md5manager.js'-File" )

        print "</pre>"

    def print_actionmenu( self ):
        print "Please select:"
        print "<ul>"
        for i in self.actions :
            print '<li><a href="?%s">%s</a></li>' % (i[1], i[2])

        print "</ul>"

    ###########################################################################################

    def install_PyLucid( self ):
        """ Installiert PyLucid von Grund auf """
        print "<h3>Install PyLucid:</h3>"
        self.print_backlink()

        d = SQL_dump( self.db )
        d.import_dump()
        #~ d.dump_data()



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
        if not self._has_all_keys( self.CGIdata, ["username","email","pass"] ):
            print '<form name="login" method="post" action="?add_admin">'
            print '<p>'
            print 'Username: <input name="username" type="text" value=""><br />'
            print 'email: <input name="email" type="text" value=""><br />'
            print 'Realname: <input name="realname" type="text" value=""><br />'
            print 'Passwort: <input name="pass" type="password" value="">(len min.8!)<br />'
            print '<strong>(Note: all fields required!)</strong><br />'
            print '<input type="submit" name="Submit" value="add admin" />'
            print '</p></form>'
            return

        print "<h3>Add Admin:</h3>"
        self.print_backlink( "add_admin" )
        print "<pre>"
        if not self.CGIdata.has_key("realname"):
            self.CGIdata["realname"] = None
        #~ print self.CGIdata["username"]
        #~ print self.CGIdata["pass"]

        usermanager = userhandling.usermanager( self.db )
        usermanager.add_user( self.CGIdata["username"], self.CGIdata["email"], self.CGIdata["pass"], self.CGIdata["realname"], admin=1 )

        print "User '%s' add." % self.CGIdata["username"]
        print "</pre>"
        self.print_saftey_info()
        print '<a href="?">back</a>'

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

    def setup_internal_pages( self ):
        for page in internal_pages:
            print "Insert page '%s' in table 'pages_internal'" % page["name"]
            try:
                self.db.insert( "pages_internal", page )
            except Exception, e:
                print "Error: '%s'" % e
            print


    def sql_dump( self ):
        print "<h3>SQL (experimental!)</h3>"
        if not self.CGIdata.has_key("sql_commands"):
            self.print_backlink()
            print '<form name="sql_dump" method="post" action="?sql_dump">'
            print '<p>SQL command:<br/>'
            print '<textarea name="sql_commands" cols="90" rows="25"></textarea><br/>'
            print '<input type="submit" name="Submit" value="send" />'
            print '</p></form>'
            sys.exit()

        self.print_backlink( "sql_dump" )
        sql_commands = self.CGIdata["sql_commands"]
        sql_commands = sql_commands.replace( "\r\n","\n" )
        #~ sql_commands = sql_commands.replace( "\n","" )

        self.execute( sql_commands )

        print "<pre>"
        sql_commands = cgi.escape( sql_commands )
        print sql_commands
        print "-"*80
        print sql_commands.encode("String_Escape")
        print "</pre>"

    ###########################################################################################
    ###########################################################################################

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
    print "Content-type: text/html\n"
    PyLucid_setup()



