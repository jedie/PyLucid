#!/usr/bin/python
# -*- coding: UTF-8 -*-

"install additional PyLucid SQL-Tables"

__version__ = "v0.0.3"

__history__ = """
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
from system import SQL, sessiondata, userhandling, config
from system.config import dbconf







SQL_make_tables = [
{
    "name"      : "pages_internal",
    "command"   :
"""CREATE TABLE IF NOT EXISTS `%(dbTablePrefix)spages_internal` (
`name` VARCHAR( 50 ) NOT NULL ,
`markup` VARCHAR( 50 ) NOT NULL ,
`content` TEXT NOT NULL ,
PRIMARY KEY ( `name` )
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
) AUTO_INCREMENT=2 COMMENT = 'PyLucid - Userdata with md5-JavaScript-Password';"""
},
{
    "name"      : "session_data",
    "command"   :
"""
CREATE TABLE `%(dbTablePrefix)ssession_data` (
`session_id` varchar(32) NOT NULL default '',
`timestamp` int(15) NOT NULL default '0',
`ip` varchar(15) NOT NULL default '',
`domain_name` varchar(50) NOT NULL default '',
`session_data` text NOT NULL,
PRIMARY KEY  (`session_id`),
KEY `session_id` (`session_id`)
) COMMENT='Python-SQL-CGI-Sessionhandling';"""
}
]


internal_pages = [
{
    "name"      : "login_form",
    "markup"    : "none",
    "content"   :
"""<p>
    <h2>PyLucid - LogIn:</h2>
    <script src="%(md5)s" type="text/javascript"></script>
    <script src="%(md5manager)s" type="text/javascript"></script>
    <noscript>Javascript is needed!</noscript>
    <form name="login" method="post" action="%(url)s">
    <p>
        <input name="rnd" type="hidden" value="%(rnd)s">
        <input name="use_md5login" type="hidden" value="0">
        User:
        <input name="user" type="text" value=""><br />
        Passwort:
        <input name="pass" type="password" value=""><br />
        md5pass:
        <input name="md5pass1" value="" type="text" size="34" maxlength="32" />
        <input name="md5pass2" value="" type="text" size="34" maxlength="32" />
        <br />
        <a href="javascript:md5login();">MD5 LogIn</a>
    </p>
    </form>
</p>"""
},
{
    "name"      : "edit_page",
    "markup"    : "none",
    "content"   :
"""%(status_msg)s
<form name="login" method="post" action="%(url)s">
  <p>Page: &quot;%(name)s&quot;:<br>
    <textarea name="content" cols="90" rows="20" wrap="VIRTUAL">%(content)s</textarea>
    <br />
    <input type="submit" name="Submit" value="preview" />
    <input type="submit" name="Submit" value="save" />
    <input type="reset" name="abort" onClick="javacript:window.location.href='?%(name)s'" value="abort" />
    Encoding: <select name="encoding" id="encoding">%(encoding_option)s</select>
    <input type="submit" name="Submit" value="encode from DB" />
  </p>
  <table border="0" cellspacing="1" cellpadding="1">
    <tr>
      <td> trivial modifications:</td>
      <td><input name="trivial" type="checkbox" id="trivial" value="1" />
        ( If checked the side will not archived. )</td>
    </tr>
    <tr>
      <td>Edit summary: </td>
      <td><input name="summary" type="text" value="%(summary)s" id="summary" size="50" maxlength="50" /></td>
    </tr>
  </table>
  <h4>Page Details</h4>
  <table border="0">
    <tr>
      <td>page name:</td>
      <td><input name="name" type="text" value="%(name)s" size="50" maxlength="50"></td>
    </tr>
    <tr>
      <td>page title:</td>
      <td><input name="title" type="text" value="%(title)s" size="50" maxlength="50"></td>
    </tr>
    <tr>
      <td>keywords: </td>
      <td><input name="keywords" type="text" value="%(keywords)s" size="70" maxlength="255"></td>
    </tr>
    <tr>
      <td>description: </td>
      <td><input name="description" type="text" value="%(description)s" size="70" maxlength="255"></td>
    </tr>
  </table>
  <h4>Page Controls</h4>
  <table border="0">
    <tr>
      <td>Parent Page: </td>
      <td><select name="parent" id="parent">%(parent_option)s</select></td>
    </tr>
    <tr>
      <td>Template:</td>
      <td><select name="template" id="template">%(template_option)s</select></td>
    </tr>
    <tr>
      <td>Style: </td>
      <td><select name="style">%(style_option)s</select></td>
    </tr>
    <tr>
      <td>Markup: </td>
      <td><select name="markup">%(markup_option)s</select></td>
    </tr>
    <tr>
      <td>Page Owner: </td>
      <td><select name="ownerID" id="ownerID">%(ownerID_option)s</select></td>
    </tr>
  </table>
  <h4>Page Permissions</h4>
  <table border="0" cellspacing="1" cellpadding="1">
    <tr>
      <td>Editable by Group: </td>
      <td><select name="permitEditGroupID" id="permitEditGroupID">%(permitEditGroupID_option)s</select></td>
    </tr>
    <tr>
      <td>Viewable by Group:</td>
      <td><select name="permitViewGroupID" id="permitViewGroupID">%(permitViewGroupID_option)s</select></td>
    </tr>
    <tr>
      <td>showlinks</td>
      <td><input name="showlinks" type="checkbox" id="showlinks" value="1"%(showlinks)s></td>
    </tr>
    <tr>
      <td>permit view public</td>
      <td><input name="permitViewPublic" type="checkbox" id="permitViewPublic" value="1"%(permitViewPublic)s></td>
    </tr>
  </table>
</form>"""
}
]


SQL_insert_internal_pages = """INSERT INTO `%(dbTablePrefix)spages_internal` ( `name` , `markup` , `content` )
VALUES (
'%(name)s', '%(markup)s', '%(content)s'
);"""



HTML_head = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>PyLucid Setup</title>
<meta name="robots"                    content="noindex,nofollow" />
<meta http-equiv="Content-Type"        content="text/html; charset=utf-8" />
</head>
<body>
<h2>PyLucid Setup %s</h2>""" % __version__



class PyLucid_setup:
    def __init__( self ):

        self.db = SQL.db()

        self.CGIdata        = sessiondata.CGIdata( self.db, detect_page = False )

        print HTML_head

        #~ print "<p>CGI-data debug: '%s'</p>" % self.CGIdata

        self.actions = [
                (self.setup_db,       "setup_db",    "setup database (create all Tables/internal pages)"),
                (self.update_db,      "update_db",   "update internal pages (set all internal pages to default)"),
                (self.add_admin,      "add_admin",   "add admin"),
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
        print "-"*80
        print "If DB-connection fail check config in './system/config.py' first!"
        print "test DB-connection use './DBtest.py'."
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
                    "dbTablePrefix" : dbconf["dbTablePrefix"]
                }
            print "Insert table '%s' in DB" % table["name"]
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
            #~ page_id = self.db.side_id_by_name( page["name"] )
            #~ print page_id
            #~ page_id = self.db.select(
                    #~ select_items    = ["id"],
                    #~ from_table      = "pages_internal",
                    #~ where           = ("name",page["name"])
                #~ )[0]
            #~ print page_id

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


