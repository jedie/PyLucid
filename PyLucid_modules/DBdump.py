#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Erzeugt einen Download des SQL Dumps
http://dev.mysql.com/doc/mysql/de/mysqldump.html
"""

__version__="0.0.2"

__history__="""
v0.0.2
    - Großer Umbau: Anderes Menü, anderer Aufruf von mysqldump, Möglichkeiten Dump-Parameter anzugeben
v0.0.1
    - Erste Version
"""

import cgitb;cgitb.enable()
import os,sys,cgi, time




#_______________________________________________________________________
# Module-Manager Daten für den page_editor

URL_parameter       = "DB_dump"

class module_info:
    """Pseudo Klasse: Daten f���den Module-Manager"""
    data = {
        URL_parameter : {
            "txt_menu"      : URL_parameter,
            "txt_long"      : "dump all DB data",
            "section"       : "admin sub menu",
            "category"      : "administation",
            "must_login"    : True,
            "must_admin"    : True,
        },
    }


#_______________________________________________________________________





class sql_dump:
    def __init__( self, PyLucid ):
        self.CGIdata    = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.config     = PyLucid["config"]
        self.db         = PyLucid["db"]
        self.tools      = PyLucid["tools"]

        self.out = self.tools.out_buffer()

        self.actions = [
            ( "make_dump",      "make SQL dump",            self.make_dump ),
            ( "display_dump",   "display SQL dump, only",   self.display_dump ),
            ( "help",           "display mysqldump help",   self.display_help ),
            #~ ( "download_dump",  "download dump",            self.download_dump )
        ]

    def action( self ):
        try:
            action = self.CGIdata["action"]
        except KeyError:
            self.menu()
            return self.out.get()

        # Das Menü wird immer angezeigt
        self.menu()
        self.out( "<hr>" )

        for item in self.actions:
            if action == item[0]:
                # Aktion ausführen
                item[2]()
                # Ausgabewerte zurückliefern
                return self.out.get()

        return "action '%s' unknown!" % cgi.escape( action )


    def menu( self ):
        """ Menü für Aktionen generieren """
        self.out( "<h3>DB dump v%s</h3>" %  __version__ )

        self.out( '<form name="login" method="post" action="%s?command=%s&page_id=%s">' % (
            self.config.system.real_self_url, URL_parameter, self.CGIdata["page_id"]
        ))
        self.out( '<p class="db_dump">' )
        self.out( 'character set:' )
        self.out( '<select name="character-set" size="1">' )
        self.out( self.tools.html_option_maker().build_from_list(
            ["latin1","utf8"],
            selected_item = "latin1" )
        )
        self.out( '</select>' )
        self.out( '<br/>' )

        self.out( 'compatible:' )
        self.out( '<select name="compatible" size="1">' )
        self.out( self.tools.html_option_maker().build_from_list(
            ["ansi", "mysql323", "mysql40", "postgresql", "oracle", "mssql", "db2", "maxdb",
            "no_key_options", "no_table_options", "no_field_options"],
            selected_item = "mysql40" )
        )
        self.out( '</select>' )
        self.out( "<br/>(Requires MySQL server v4.1.0 or higher)<br/>" )

        self.out( '<br/>' )

        self.out( 'other options:' )
        self.out( '<input name="options" value="--extended-insert --skip-opt" size="50" maxlength="50" type="text">' )

        self.out( '</p>' )

        self.out( '<p>' )
        for action in self.actions:
            self.out(
                '<button type="submit" name="action" value="%s">%s</button>&nbsp;&nbsp;' % (
                    action[0], action[1]
                )
            )
        self.out('</p>')

        self.out('</form>')

    #_______________________________________________________________________

    def make_dump( self ):
        """
        Erstellt den SQL Dump
        """
        self.out( "<h3>make SQL dump</h3>" )

        self.out( "<pre>" )

        command = self._get_sql_command()

        out_data = self._process( command, "/usr/bin/", timeout = 10 )
        if out_data == False:
            # Fehler beim ausführen aufgetreten -> Abbruch, Seite wird angezeigt
            return

        print 'Content-Disposition: attachment; filename=%s_%s%s.sql' % (
            time.strftime( "%Y%m%d" ), self.config.dbconf["dbTablePrefix"], self.config.dbconf["dbDatabaseName"]
        )
        print 'Content-Transfer-Encoding: binary'
        print 'Content-Type: application/octet-stream; charset=utf-8\n'

        # Zusatzinfo's in den Dump "einblenden"
        sys.stdout.write( self.additional_dump_info( command.replace( self.config.dbconf["dbPassword"], "***" ) ) )
        sys.stdout.write( out_data )

        sys.exit()

    #_______________________________________________________________________

    def display_dump( self ):
        """
        Erstellt den SQL Dump und zeigt ihn im Browser
        """
        self.out( "<h3>display SQL dump</h3>" )

        command = self._get_sql_command()

        self.out( "<p>SQL-Command:</p><pre>%s</pre>" % command.replace( self.config.dbconf["dbPassword"], "***" ) )

        self.out( "<pre>" )

        out_data = self._process( command, "/usr/bin/", timeout = 10 )
        if out_data == False:
            # Fehler beim ausführen aufgetreten -> Abbruch, Seite wird angezeigt
            return

        self.out( cgi.escape(out_data) )

        self.out( "</pre>" )

    #_______________________________________________________________________

    def display_help( self ):
        self.out( "<h3>mysqldump --help</h3>" )

        self.out( "<pre>" )

        out_data = self._process( "mysqldump --help", "/usr/bin/", timeout = 1 )
        if out_data == False:
            # Fehler beim ausführen aufgetreten -> Abbruch, Seite wird angezeigt
            return

        self.out( out_data )
        self.out( "</pre>" )

    #_______________________________________________________________________

    def error( self, *txt ):
        print "Content-type: text/html; charset=utf-8\r\n\r\n"
        print "<h1>SQL dump Fehler:</h1>"
        print "<br/>".join( [cgi.escape(str(i)) for i in txt] )
        sys.exit()

    def additional_dump_info( self, sql_command ):
        txt = "-- ------------------------------------------------------\n"
        txt += "-- Dump created %s with PyLucid's %s v%s\n" % (
            time.strftime("%d.%m.%Y, %H:%M"), os.path.split(__file__)[1], __version__
            )
        txt += "--\n"
        txt += "-- The SQLcommand:\n"
        txt += "-- %s\n" % sql_command
        txt += "--\n"
        txt += "-- This file should be encoded in utf8 !\n"
        txt += "-- ------------------------------------------------------\n"
        return txt

    def _get_sql_command( self ):
        tablenames = " ".join( self.db.get_tables() )
        #~ tablenames = "%spages" % self.config.dbconf["dbTablePrefix"]
        return "/usr/bin/mysqldump --default-character-set=%(cs)s --compatible=%(cp)s %(op)s -u%(u)s -p%(p)s -h%(h)s %(n)s --tables %(tn)s" % {
            "cs" : self.CGIdata["character-set"],
            "cp" : self.CGIdata["compatible"],
            "op" : self.CGIdata["options"],
            "u"  : self.config.dbconf["dbUserName"],
            "p"  : self.config.dbconf["dbPassword"],
            "h"  : self.config.dbconf["dbHost"],
            "n"  : self.config.dbconf["dbDatabaseName"],
            "tn" : tablenames,
        }

    #_______________________________________________________________________

    def _process( self, command, cwd, timeout ):
        #~ process = self.tools.subprocess2(
            #~ command, cwd, timeout
        #~ )
        try:
            process = self.tools.subprocess2(
                command, cwd, timeout
            )
        except Exception,e:
            self.out( "subprocess Error:", e )
            return False
        else:
            if process.returncode != 0 and process.returncode != None:
                self.out( "subprocess Error!" )
                self.out( "Returncode:", process.returncode )
                self.out( "output:", process.out_data )
                return False
            #~ if process.killed == True:
                #~ self.out( "subprocess timout!" )
                #~ return False

        return process.out_data

#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid ):
    # Aktion starten
    return sql_dump( PyLucid ).action()


