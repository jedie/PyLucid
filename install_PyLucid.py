#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""PyLucid "installer"

Evtl. muß der Pfad in dem sich PyLucid's "config.py" sich befindet
per Hand angepasst werden!
"""

__version__ = "v0.0.6"

__history__ = """
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
import os, sys, cgi



# Interne PyLucid-Module einbinden
# Verzeichnis in dem PyLucid's "config.py" sich befindet, in den Pfad aufnehmen
#~ sys.path.insert( 0, os.environ["DOCUMENT_ROOT"] )
#~ sys.path.insert( 0, os.environ["DOCUMENT_ROOT"] + "cgi-bin/PyLucid" )

import config # PyLucid's "config.py"
from PyLucid_system import SQL, sessiondata, userhandling


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
## Tabellen Daten

SQL_make_tables = [
{
    "name"      : "pages_internal",
    "command"   :
"""CREATE TABLE `%(dbTablePrefix)spages_internal` (
name VARCHAR( 50 ) NOT NULL ,
markup VARCHAR( 50 ) NOT NULL ,
content TEXT NOT NULL ,
description TEXT NOT NULL ,
PRIMARY KEY ( name )
) COMMENT = 'PyLucid - internal Pages';"""
},
{
    "name"      : "md5users",
    "command"   :
"""CREATE TABLE `%(dbTablePrefix)smd5users` (
`id` INT( 11 ) NOT NULL AUTO_INCREMENT,
`name` VARCHAR( 50 ) NOT NULL ,
`realName` VARCHAR( 50 ) NOT NULL ,
`email` VARCHAR( 50 ) NOT NULL ,
`pass1` VARCHAR( 32 ) NOT NULL ,
`pass2` VARCHAR( 32 ) NOT NULL ,
`admin` TINYINT( 4 ) DEFAULT '0' NOT NULL ,
 PRIMARY KEY  (`id`),
 UNIQUE KEY `name` (`name`)
) COMMENT = 'PyLucid - Userdata with md5-JavaScript-Password';"""
},
{
    "name"      : "session_data",
    "command"   :
"""CREATE TABLE `%(dbTablePrefix)ssession_data` (
`session_id` varchar(32) NOT NULL default '',
`user_nae` varchar(32) NOT NULL default '',
`timestamp` int(15) NOT NULL default '0',
`ip` varchar(15) NOT NULL default '',
`domain_name` varchar(50) NOT NULL default '',
`session_data` text NOT NULL,
PRIMARY KEY  (`session_id`),
KEY `session_id` (`session_id`)
) COMMENT='Python-SQL-CGI-Sessionhandling';"""
},
{
    "name"      : "lucid_log",
    "command"   :
"""CREATE TABLE `%(dbTablePrefix)slog` (
  `id` int(11) NOT NULL auto_increment,
  `timestamp` datetime,
  `sid` varchar(50) NOT NULL default '-1',
  `user_name` varchar(50) default NULL,
  `ip` varchar(50) default NULL,
  `domain` varchar(50) default NULL,
  `message` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`id`)
) COMMENT='PyLucid - Logging' ;"""
}
]


#__________________________________________________________________________
## Seiten Daten


internal_pages = [
{
    "name"        : "login_form",
    "description" : "The Login Page.",
    "markup"      : "none",
    "content"     :
"""<h2>PyLucid - LogIn:</h2>
<script src="%(md5)s" type="text/javascript"></script>
<script src="%(md5manager)s" type="text/javascript"></script>
<noscript>Javascript is needed!</noscript>
<form name="login" method="post" action="%(url)s">
    <p>
        User:
        <input name="user" type="text" value=""><br />
        Passwort:
        <input name="pass" type="password" value=""><br />
        md5pass:
        <input name="md5pass1" value="" type="text" size="34" maxlength="32" />
        <input name="md5pass2" value="" type="text" size="34" maxlength="32" />
        <br />
        <input name="rnd" type="hidden" value="%(rnd)s">
        <input name="use_md5login" type="hidden" value="0">
        <a href="javascript:md5login();">MD5 LogIn</a>
    </p>
</form>
<script type="text/javascript">
    document.login.user.focus();
</script>
"""
},
{
    "name"        : "admin_sub_menu",
    "description" : "Administration sub menu",
    "markup"      : "none",
    "content"     :
"""<h2>Administration Sub-Menu</h2>
<lucidTag:admin_sub_menu_list/>"""
},
{
    "name"        : "edit_style",
    "description" : "Page to edit a stylesheet",
    "markup"      : "none",
    "content"     :
"""<h2>Edit CSS stylesheet</h2>
<form method="post" action="%(url)s">
    <p>
        Name: <strong>&quot;%(name)s&quot;</strong>:<br/>
        <textarea wrap="off" id="edit_style" name="content" style="width: 100%%;" rows="20" accept-charset="UTF-8">%(content)s</textarea><br />
        Description: <input name="description" type="text" style="width: 100%%;" value="%(description)s"><br />
        <input type="submit" name="Submit" value="save" />
        <input type="reset" name="abort" onClick="javacript:window.location.href='%(back)s'" value="abort" />
    </p>
</form>"""
},
{
    "name"        : "edit_template",
    "description" : "Page to edit a template",
    "markup"      : "none",
    "content"     :
"""<h2>Edit template</h2>
<form method="post" action="%(url)s">
    <p>
        Name: <strong>&quot;%(name)s&quot;</strong>:<br/>
        <textarea wrap="off" id="edit_style" name="content" style="width: 100%%;" rows="20" accept-charset="UTF-8">%(content)s</textarea><br />
        Description: <input name="description" type="text" style="width: 100%%;" value="%(description)s"><br />
        <input type="submit" name="Submit" value="save" />
        <input type="reset" name="abort" onClick="javacript:window.location.href='%(back)s'" value="abort" />
    </p>
</form>"""
},
{
    "name"        : "edit_internal_page",
    "description" : "Page to edit a internal page",
    "markup"      : "none",
    "content"     :
"""<h2>Edit internal page</h2>
<form method="post" action="%(url)s">
    <p>
        Name: <strong>&quot;%(name)s&quot;</strong>:<br/>
        <textarea wrap="off" id="edit_internal_page" name="content" style="width: 100%%;" rows="20" accept-charset="UTF-8">%(content)s</textarea><br />
        Description: <input name="description" type="text" style="width: 100%%;" value="%(description)s"><br />
        <input type="submit" name="Submit" value="save" />
        <input type="reset" name="abort" onClick="javacript:window.location.href='%(back)s'" value="abort" />
    </p>
</form>"""
},
{
    "name"        : "edit_page",
    "description" : "Page to edit a normal Content-Page",
    "markup"      : "none",
    "content"     :
"""%(status_msg)s
<style type="text/css">
    .edit_page {
        line-height:1.5em;
    }
    .edit_page input, .edit_page select {
        position: absolute;
        left: 28em;

    }
    .resize_buttons a {
        text-decoration:none;
    }
    #hr_textarea {
        clear: both;
        margin: 1px;
        padding: 1px;
        border: none;
    }
</style>
<form name="login" method="post" action="%(url)s">
  <p>Page: <strong>&quot;%(name)s&quot;</strong>:<br>
    <textarea id="page_content" name="content" rows="20" accept-charset="UTF-8">%(content)s</textarea>
    <hr id="hr_textarea">
    <span class="resize_buttons">
        <a href="JavaScript:resize_big();" alt="bigger">&nbsp;+&nbsp;</a>
        <a href="JavaScript:resize_small();">&nbsp;-&nbsp;</a>
        &nbsp;&nbsp;
    </span>
    <input type="submit" name="Submit" value="preview" />
    <input type="submit" name="Submit" value="save" />
    <input type="reset" name="abort" onClick="javacript:window.location.href='?%(name)s'" value="abort" />
    ||| <input type="submit" name="Submit" value="encode from DB" />
    <select name="encoding" id="encoding">%(encoding_option)s</select>
  </p>
  <p>
    trivial modifications: <input name="trivial" type="checkbox" id="trivial" value="1" />( If checked the side will not archived. )<br/>
    Edit summary: <input name="summary" type="text" value="%(summary)s" id="summary" size="50" maxlength="50" />
  </p>
  <h4>Page Details</h4>
  <p class="edit_page">
    page name:    <input name="name" type="text" value="%(name)s" size="50" maxlength="50"><br/>
    page title:   <input name="title" type="text" value="%(title)s" size="50" maxlength="50"><br/>
    keywords:     <input name="keywords" type="text" value="%(keywords)s" size="70" maxlength="255"><br/>
    description:  <input name="description" type="text" value="%(description)s" size="70" maxlength="255"><br/>
  </p>
  <h4>Page Controls</h4>
  <p class="edit_page">
    Parent Page:    <select name="parent" id="parent">%(parent_option)s</select><br/>
    Template:       <select name="template" id="template">%(template_option)s</select><br/>
    Style:          <select name="style">%(style_option)s</select><br/>
    Markup:         <select name="markup">%(markup_option)s</select><br/>
    Page Owner:     <select name="ownerID" id="ownerID">%(ownerID_option)s</select><br/>
  </p>
  <h4>Page Permissions</h4>
  <p class="edit_page">
    Editable by Group:  <select name="permitEditGroupID" id="permitEditGroupID">%(permitEditGroupID_option)s</select><br/>
    Viewable by Group:  <select name="permitViewGroupID" id="permitViewGroupID">%(permitViewGroupID_option)s</select><br/>
    showlinks:          <input name="showlinks" type="checkbox" id="showlinks" value="1"%(showlinks)s><br/>
    permit view public: <input name="permitViewPublic" type="checkbox" id="permitViewPublic" value="1"%(permitViewPublic)s><br/>
  </p>
</form>
<script type="text/javascript">
    // Skript zum größer und kleiner machen des Eingabefeldes
    textarea = document.getElementById("page_content");
    hr_textarea = document.getElementById("hr_textarea");
    old_cols = textarea.cols;
    old_rows = textarea.rows;
    function resize_big() {
        textarea.style.position = "absolute";
        textarea.style.left = "1em";
        textarea.style.top = "1em";
        textarea.cols = textarea.cols*1.4;
        textarea.rows = textarea.rows*1.75;

        hr_textarea.style.margin = "26em";
    }
    function resize_small() {
        textarea.style.position = "relative";
        textarea.style.left = "0px";
        textarea.style.top = "0px";
        textarea.cols = old_cols;
        textarea.rows = old_rows;
        hr_textarea.style.margin = "1px";
    }
</script>
"""
}
]


SQL_insert_internal_pages = """INSERT INTO `%(dbTablePrefix)spages_internal` ( name, markup, content, description )
VALUES (
'%(name)s', '%(markup)s', '%(content)s'
);"""



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
                (self.convert_db,     "convert_db",  "convert DB data from PHP-LucidCMS to PyLucid Format"),
                (self.setup_db,       "setup_db",    "setup database (create all Tables/internal pages)"),
                (self.update_db,      "update_db",   "update internal pages (set all internal pages to default)"),
                (self.add_admin,      "add_admin",   "add admin (needed für secure MD5-Login!)"),
                (self.sql_dump,       "sql_dump",    "SQL dump (experimental)"),
                (self.convert_locals, "locals",      "convert locals (ony preview!)"),
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

    def add_admin( self ):
        print "<h3>Add Admin:</h3>"

        if not self._has_all_keys( self.CGIdata, ["username","email","pass"] ):
            self.print_backlink()
            print '<form name="login" method="post" action="?add_admin">'
            print '<p>'
            print 'Username: <input name="username" type="text" value=""><br />'
            print 'email: <input name="email" type="text" value=""><br />'
            print 'Realname: <input name="realname" type="text" value=""><br />'
            print 'Passwort: <input name="pass" type="password" value="">(len min.8!)<br />'
            print '<strong>(Note: all fields required!)</strong><br />'
            print '<input type="submit" name="Submit" value="send" />'
            print '</p></form>'
            sys.exit()

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
        print '<a href="?">back</a>'

    ###########################################################################################
    ###########################################################################################

    def setup_db( self ):
        print "<h3>Setup Database:</h3>"
        self.print_backlink()
        print "<pre>"
        print "="*80

        self.setup_tables()
        self.setup_internal_pages()

        print "="*80
        print "Setup finally!"
        print "</pre>"
        self.print_backlink()
        self.print_saftey_info()

    def setup_tables( self ):
        for table in SQL_make_tables:
            SQLcommand = table["command"] % {
                    "dbTablePrefix" : config.dbconf["dbTablePrefix"]
                }
            print "Insert table '%s' in DB" % table["name"]
            #~ print "***\n%s\n***" % SQLcommand
            self.execute( SQLcommand )
            print

    def setup_internal_pages( self ):
        for page in internal_pages:
            print "Insert page '%s' in table 'pages_internal'" % page["name"]
            try:
                self.db.insert( "pages_internal", page )
            except Exception, e:
                print "Error: '%s'" % e
            print

    ###########################################################################################
    ###########################################################################################

    def update_db( self ):
        print "<h3>set all internal pages to default.</h3>"
        self.print_backlink()
        print "<pre>"
        for page in internal_pages:
            print "update page '%s' in table 'pages_internal'" % page["name"]
            try:
                #~ self.db.update( "pages_internal", page )
                self.db.update(
                    table   = "pages_internal",
                    data    = page,
                    where   = ("name",page["name"]),
                    limit   = 1
                )
            except Exception, e:
                print "Error: '%s'" % e
            print
        print "</pre>"

    ###########################################################################################
    ###########################################################################################

    def sql_dump( self ):
        print "<h3>SQL (experimental!)</h3>"
        if not self.CGIdata.has_key("sql_commands"):
            self.print_backlink()
            print '<form name="sql_dump" method="post" action="?sql_dump">'
            print '<p>SQL command:<br/>'
            print '<textarea name="sql_commands" cols="90" rows="20"></textarea><br/>'
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
        print "<h3>After setup: Delete this file (%s) on the server !!!</h3>" % os.environ["SCRIPT_NAME"]


if __name__ == "__main__":
    print "Content-type: text/html\n"
    PyLucid_setup()



