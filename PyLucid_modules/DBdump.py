#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Erzeugt einen Download des SQL Dumps
http://dev.mysql.com/doc/mysql/de/mysqldump.html
"""

__version__="0.0.1"

__history__="""
v0.0.1
    - Erste Version
"""

import cgitb;cgitb.enable()
import os,sys,cgi, time
import tempfile




#_______________________________________________________________________
# Module-Manager Daten für den page_editor

URL_parameter       = "DB_dump"
make_dump_url       = "?command=%s&action=make_dump" % URL_parameter
display_help_url    = "?command=%s&action=help" % URL_parameter
download_dump_url   = "?command=%s&action=download_dump" % URL_parameter

back_link = '<a href="?command=%s">back</a>' % URL_parameter

class module_info:
    """Pseudo Klasse: Daten f���den Module-Manager"""
    data = {
        URL_parameter : {
            "txt_menu"      : "DB dump",
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

    def action( self ):
        try:
            action = self.CGIdata["action"]
        except KeyError:
            self.menu()
            return self.out.get()

        if action == "make_dump":
            self.make_dump()
        elif action == "download_dump":
            self.download_dump()
        elif action == "help":
            self.display_help()
        else:
            return "action '%s' unknown!" % cgi.escape( action )

        return self.out.get()

    def _make_tempname( self, basename ):
        """ Generiert einen TEMP-Dateinamen inkl. Pfad """
        return os.path.join(
            tempfile.gettempdir(), basename + "." + tempfile.gettempprefix()
        )

    def menu( self ):
        """ Menü für Aktionen generieren """
        self.out( "<h3>DB dump v%s</h3>" %  __version__ )
        self.out( '<a href="%s">download SQL dump</a><br>' % make_dump_url )
        self.out( '<a href="%s">Archive a SQL dump on FTP-Server</a><br>' % make_dump_url )
        self.out( '<a href="%s">display mysqldump --help</a><br>' % display_help_url )

    #_______________________________________________________________________

    def check_dumpfile( self, tmpfilename ):
        """
        Prüft ob die Temp-Datei schon existiert, wenn ja wird versucht diese zu löschen
        """
        if os.path.isfile( tmpfilename ):
            self.out( "Notice: Temp-File '%s' exists." % tmpfilename )
            try:
                os.remove( tmpfilename )
            except Exception, e:
                self.out( "ERROR: Can't delete Temp-File:", e )
                self.out( "</pre>" )
                return False

        return True

    def make_dump( self ):
        """
        Erstellt den SQL Dump
        """
        self.out( "<h3>make SQL dump</h3>" )

        self.out( "<pre>" )

        temp_filename = self._make_tempname( "sqldump" )

        if self.check_dumpfile( temp_filename ) == False:
            # Vorhandene Temp-Datei konnte nicht gelöscht werden :(
            return self.out.get()

        tablenames = " ".join( self.db.get_tables() )

        command = "/usr/bin/mysqldump --extended-insert --skip-opt -v -u%(u)s -p%(p)s -h%(h)s %(n)s --tables %(tn)s --result-file=%(tf)s" % {
            "u"  : self.config.dbconf["dbUserName"],
            "p"  : self.config.dbconf["dbPassword"],
            "h"  : self.config.dbconf["dbHost"],
            "n"  : self.config.dbconf["dbDatabaseName"],
            "tn" : tablenames,
            "tf" : temp_filename,
        }

        out_data = self._process( command, "/usr/bin/", timeout = 10 )
        if out_data == False:
            # Fehler beim ausführen aufgetreten -> Abbruch, Seite wird angezeigt
            return

        # von mysqldump erzeuge Datei "prüfen"
        try:
            dumpsize = os.path.getsize( temp_filename )
        except OSError, e:
            self.out( "ERROR:", e )
            return
        else:
            if dumpsize == 0:
                self.out( "Error with Dumpfile (size 0 Bytes) !" )
                return

        try:
            tf = file( temp_filename, "r" )
        except IOError:
            self.out( "Error Reading dumpfile: '%s'!" % temp_filename )
            return

        print 'Content-Disposition: attachment; filename=%s_%s.sql' % (
            time.strftime( "%Y%m%d" ), self.config.dbconf["dbDatabaseName"]
        )
        print 'Content-Transfer-Encoding: binary'
        print 'Content-Type: application/octet-stream; charset=utf-8\n'

        # Zusatzinfo's in den Dump "einblenden"
        sys.stdout.write( self.additional_dump_info() )

        while 1:
            data = tf.read( 8192 )
            if data == "": break
            sys.stdout.write( data )
        tf.close()

        os.remove( temp_filename )

        sys.exit()

    def error( self, *txt ):
        print "Content-type: text/html; charset=utf-8\r\n\r\n"
        print "<h1>SQL dump Fehler:</h1>"
        print "<br/>".join( [cgi.escape(str(i)) for i in txt] )
        sys.exit()

    def additional_dump_info( self ):
        txt = "-- ------------------------------------------------------\n"
        txt += "-- Dump created %s with PyLucid's %s v%s\n" % (
            time.strftime("%d.%m.%Y, %H:%M"), os.path.split(__file__)[1], __version__
            )
        txt += "-- ------------------------------------------------------\n"
        return txt

    #_______________________________________________________________________

    def display_help( self ):
        self.out( "<h3>mysqldump --help</h3>" )

        self.out( back_link )

        self.out( "<pre>" )

        out_data = self._process( "mysqldump --help", "/usr/bin/", timeout = 1 )
        if out_data == False:
            # Fehler beim ausführen aufgetreten -> Abbruch, Seite wird angezeigt
            return

        self.out( out_data )
        self.out( "</pre>" )

        self.out( back_link )

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

