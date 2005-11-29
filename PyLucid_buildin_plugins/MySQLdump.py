#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Erzeugt einen Download des SQL Dumps
http://dev.mysql.com/doc/mysql/de/mysqldump.html
"""

__version__="0.2.2"

__history__="""
v0.2.2
    - Nutzt die module_manager Einstelung "sys_exit", damit der Dumpdownload richtig beendet wird
    - In additional_dump_info ist in sys.version ein \n Zeichen, welches nun rausfliegt.
v0.2.1
    - Anpassung an self.db.print_internal_page()
v0.2.0
    - HTML-Ausgaben nun über interne Seite
v0.1.2
    - Umbenennung in MySQLdump, weil's ja nur für MySQL geht...
    - NEU: Nun kann man auch den Pfad zu mysqldump angeben. Standard ist "." (aktuelles Verzeichnis)
        damit wird mysqldump im Pfad gesucht. Das klappt nun auch unter Windows
v0.1.1
    - NEU: Man kann nun genau auswählen was von welcher Tabelle man haben will
v0.1.0
    - Anpassung an Module-Manager
    - Umau an einigen Stellen
v0.0.4
    - Es ist nun möglich kein "--compatible=" Parameter zu benutzen (wichtig bei MySQL server <v4.1.0)
v0.0.3
    - Module-Manager Angabe "direct_out" hinzugefügt, damit der Download des
      Dumps auch funktioniert.
v0.0.2
    - Großer Umbau: Anderes Menü, anderer Aufruf von mysqldump, Möglichkeiten Dump-Parameter anzugeben
v0.0.1
    - Erste Version
"""

__todo__ = """
verwendet noch Buttons!
"""

import cgitb;cgitb.enable()
import os,sys,cgi, time




class MySQLdump:

    global_rights = {
            "must_login"    : True,
            "must_admin"    : True,
    }

    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "menu" : global_rights,

        "display_help"      : global_rights,
        "display_dump"      : global_rights,
        "display_command"   : global_rights,
        "download_dump" : {
            "must_login"    : True,
            "must_admin"    : True,
            "direct_out"    : True,
            "sys_exit"      : True, # Damit ein sys.exit() auch wirklich fuktioniert
        }
    }

    def __init__( self, PyLucid ):
        self.CGIdata    = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.config     = PyLucid["config"]
        self.db         = PyLucid["db"]
        self.tools      = PyLucid["tools"]

    def menu( self ):
        """ Menü für Aktionen generieren """
        default_no_data = ["log", "session_data"]
        default_no_data = [self.config.dbconf["dbTablePrefix"] + i for i in default_no_data]

        table_data = ""
        for name in self.db.get_tables():
            if name in default_no_data:
                structure = ' checked="checked"'
                complete = ''
            else:
                structure = ''
                complete = ' checked="checked"'

            table_data += '<tr>\n'
            table_data += '\t<td>%s</td>\n' % name
            table_data += '\t<td><input type="radio" name="%s" value="ignore" /></td>\n' % name
            table_data += '\t<td><input type="radio" name="%s" value="structure"%s /></td>\n' % (
                name, structure
            )
            table_data += '\t<td><input type="radio" name="%s" value="complete"%s /></td>\n' % (
                name, complete
            )
            table_data += '</tr>\n'

        self.actions = [
            ( "download_dump",  "download dump"),
            ( "display_dump",   "display SQL dump"),
            ( "display_help",   "mysqldump help" ),
            ( "display_command","display mysqldump command" ),
        ]
        buttons = ""
        for action in self.actions:
            buttons += '<button type="submit" name="action" value="%s">%s</button>&nbsp;&nbsp;\n' % (
                    action[0], action[1]
                )

        self.db.print_internal_page(
            internal_page_name  = "MySQL_dump",
            page_dict           = {
                "version"       : __version__,
                "tables"        : table_data,
                "url"           : self.command_url,
                "buttons"       : buttons
            }
        )

    #_______________________________________________________________________

    def download_dump( self ):
        """
        Erstellt den SQL Dump und bietet diesen direk zum Download an
        """
        command_list = self._get_sql_commands()
        output = self._run_command_list( command_list, timeout = 120, header=True )

        if output == False:
            # Ein Fehler ist aufgereten, Meldung wurden schon ausgegeben
            print '<a href="JavaScript:history.back();">back</a>'
            sys.exit()

        # Zusatzinfo's in den Dump "einblenden"
        output = self.additional_dump_info() + output

        print 'Content-Length:  %s' % len( output )
        print 'Content-Disposition: attachment; filename=%s_%s%s.sql' % (
            time.strftime( "%Y%m%d" ), self.config.dbconf["dbTablePrefix"], self.config.dbconf["dbDatabaseName"]
        )
        print 'Content-Transfer-Encoding: binary'
        print 'Content-Type: application/octet-stream; charset=utf-8\n'
        #~ print "Content-type: text/html; charset=utf-8\n"
        sys.stdout.write( output )
        sys.exit()

    #_______________________________________________________________________

    def display_dump( self ):
        """
        Erstellt den SQL Dump und zeigt ihn im Browser
        """
        print '<a href="JavaScript:history.back();">back</a>'

        command_list = self._get_sql_commands()
        start_time = time.time()
        output = self._run_command_list( command_list, timeout = 60 )
        if output == False:
            # Ein Fehler ist aufgereten, Meldunge wurden schon ausgegeben
            return

        print "<p><small>(mysqldump duration %.2f sec. - size: %s Bytes)</small></p>" % (
            (time.time() - start_time), self.tools.formatter( len(output), format="%0i" )
        )

        output = self.additional_dump_info() + output
        print "<pre>%s</pre>" % cgi.escape( output )

        print '<a href="JavaScript:history.back();">back</a>'

    #_______________________________________________________________________

    def display_help( self ):
        """
        Zeigt die Hilfe von mysqldump an
        """
        command_list = ["mysqldump --help"]

        print '<p><a href="JavaScript:history.back();">back</a></p>'

        output = self._run_command_list( command_list, timeout = 2 )
        if output == False:
            # Fehler aufgereten
            return

        print "<pre>%s</pre>" % output

        print '<a href="JavaScript:history.back();">back</a>'

    #_______________________________________________________________________

    def display_command( self ):
        """
        mysqldump Kommandos anzeigen, je nach Formular-Angaben
        """

        mysqldump_path = self.CGIdata["mysqldump_path"]
        print "<h3>Display command only:</h3>"
        print "<pre>"
        for command in self._get_sql_commands():
            print "%s>%s" % (
                mysqldump_path, command.replace(self.config.dbconf["dbPassword"],"***")
            )
        print "</pre>"
        print '<a href="JavaScript:history.back();">back</a>'


    def _get_sql_commands( self ):
        """
        Erstellt die Kommandoliste anhand der CGI-Daten bzw. des Formulars ;)
        """
        try:
            compatible = self.CGIdata["compatible"]
        except KeyError:
            compatible = ""
        else:
            compatible = " --compatible=%s" % compatible

        default_command = "mysqldump --default-character-set=%(cs)s%(cp)s %(op)s -u%(u)s -p%(p)s -h%(h)s %(n)s" % {
            "cs" : self.CGIdata["character-set"],
            "cp" : compatible,
            "op" : self.CGIdata["options"],
            "u"  : self.config.dbconf["dbUserName"],
            "p"  : self.config.dbconf["dbPassword"],
            "h"  : self.config.dbconf["dbHost"],
            "n"  : self.config.dbconf["dbDatabaseName"],
        }

        tablenames = self.db.get_tables()
        structure_tables = []
        complete_tables = []
        for table in tablenames:
            dump_typ = self.CGIdata[table]

            if dump_typ == "ignore":
                # Die Tabelle soll überhaupt nicht gesichert werden
                continue
            elif dump_typ == "structure":
                structure_tables.append( table )
            elif dump_typ == "complete":
                complete_tables.append( table )
            else:
                raise

        result = []
        if structure_tables != []:
            result.append(
                default_command + " --no-data " + " ".join( structure_tables )
            )
        if complete_tables != []:
            result.append(
                default_command + " --tables " + " ".join( complete_tables )
            )

        return result


    def _run_command_list( self, command_list, timeout, header=False ):
        """
        Abarbeiten der >command_list<
        liefert die Ausgaben zurück oder erstellt direk eine Fehlermeldung
        """
        try:
            mysqldump_path = self.CGIdata["mysqldump_path"]
        except KeyError:
            # Wurde im Formular leer gelassen
            mysqldump_path = "."

        def print_error( out_data, returncode, msg ):
            if header == True:
                # Beim Ausführen von "download dump" wurde noch kein Header ausgegeben
                print "Content-type: text/html; charset=utf-8\r\n"
            print "<h3>%s</h3>" % msg
            print "<p>Returncode: %s<br />" % returncode
            print "output:<pre>%s</pre></p>" % cgi.escape( out_data )

        result = ""
        for command in command_list:
            start_time = time.time()
            process = self.tools.subprocess2( command, mysqldump_path, timeout )
            result += process.out_data

            if process.killed == True:
                print_error(
                    result, process.returncode,
                    "Error: subprocess timeout (%.2fsec.>%ssec.)" % ( time.time()-start_time, timeout )
                )
                return False
            if process.returncode != 0 and process.returncode != None:
                print_error( result, process.returncode, "subprocess Error!" )
                return False

        return result

    #_______________________________________________________________________

    def additional_dump_info( self ):
        txt = "-- ------------------------------------------------------\n"
        txt += "-- Dump created %s with PyLucid's %s v%s\n" % (
            time.strftime("%d.%m.%Y, %H:%M"), os.path.split(__file__)[1], __version__
            )
        txt += "--\n"

        if hasattr(os,"uname"): # Nicht unter Windows verfügbar
            txt += "-- %s\n" % " - ".join( os.uname() )

        txt += "-- Python v%s\n" % sys.version.replace("\n","")

        txt += "--\n"

        command_list = ["mysqldump --version"]
        output = self._run_command_list( command_list, timeout = 1 )
        if output != False:
            # kein Fehler aufgereten
            txt += "-- used:\n"
            txt += "-- %s" % output

        txt += "--\n"
        txt += "-- This file should be encoded in utf8 !\n"
        txt += "-- ------------------------------------------------------\n"

        return txt







