#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Administration Sub-Menü : "show internals"
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.1.4"

__history__="""
v0.1.4
    - Anpassung an neuen ModuleManager
v0.1.3
    - NEU: who-Befehl
v0.1.2
    - Bei "Python Module Info" wird die Zeit angezeigt
v0.1.1
    - SQL-Teil funktioniert nun auch wieder ;)
v0.1.0
    - Kräftig überarbeitet.
    - NEU: "Display all Python Modules"
v0.0.5
    - NEU: Pfade werden nun angezeigt
    - Auf print Ausgaben halb umgestellt
v0.0.4
    - Andere Handhabung von tools
v0.0.3
    - verweinfachung in SQL_table_status() und optimize_sql_table() durch MySQLdb.cursors.DictCursor
v0.0.2
    - NEU SQL-Tabellen übersicht + Optimieren
v0.0.1
    - erste Version
"""

__todo__ = """
"""

# Python-Basis Module einbinden
import os, sys, cgi, imp, glob, time

# Dynamisch geladene Module
## import locale - internals.system_info()



# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"


#_______________________________________________________________________


class show_internals:

    def __init__( self, PyLucid ):
        self.CGIdata        = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.db             = PyLucid["db"]
        self.log            = PyLucid["log"]
        self.session        = PyLucid["session"]
        #~ self.session.debug()
        self.config         = PyLucid["config"]
        self.tools          = PyLucid["tools"]
        self.page_msg       = PyLucid["page_msg"]
        self.module_manager = PyLucid["module_manager"]
        self.URLs           = PyLucid["URLs"]

    def link( self ):
        print '<a href="%smenu">show_internals</a>' % self.URLs["action"]

    #_______________________________________________________________________

    def menu( self ):
        print "<h4>show internals v%s</h4>" % __version__
        self.module_manager.build_menu()

    #_______________________________________________________________________

    def python_modules( self ):
        print "<h3>Python Module Info</h3>"

        start_time = time.time()
        modulelist = modules_info().modulelist
        duration_time = time.time() - start_time

        print "%s Modules found in %.2fsec.:" % (len( modulelist ), duration_time )
        print '<table>'
        Link = '<a href="%s' % self.action_url
        Link += '%s">more Info</a>'

        modulelist.sort()
        for modulename in modulelist:
            #~ if modei
            print "<tr>"
            print "<td>%s</td>" % modulename
            print '<td><a href="%smodule_info&modulename=%s">more info</a></td>' % (
                self.action_url, modulename
            )
            print "</tr>"
        print "</table>"

    def module_info( self ):
        back_link = '<a href="%spython_modules">back</a>' % self.action_url
        print back_link
        try:
            module_name = self.CGIdata["modulename"]
        except KeyError, e:
            print "Error:", e
            return

        print "<h3>Modul info: '%s'</h3>" % module_name

        try:
            t = imp.find_module( module_name )
        except Exception,e:
            print "Can't import '%s':" % module_name
            print e
            return

        try:
            process = self.tools.subprocess2(
                "file %s" % t[1],
                "/",
                1
            )
        except Exception,e:
            fileinfo = "Can't get file-info: '%s'" % e
        else:
            try:
                fileinfo = process.out_data.split(":",1)[1]
            except:
                fileinfo = process.out_data

        print back_link
        print "<ul>"
        print "<li>pathname: %s</li>" % t[1]
        print "<li>description: %s</li>" % str(t[2])
        print "<li>fileinfo: %s</li>" % fileinfo
        print "</ul>"

        try:
            module = __import__( module_name )
        except Exception,e:
            print "<p>Can't import module ;(</p>"
            return
        else:
            print "<h4>help:</h4>"
            print "<pre>"
            help( module )
            print "</pre>"

        if t[2][1] == "rb":
            print "<p>(SourceCode not available. It's a binary module.)</p>"
        else:
            try:
                print "<h4>SourceCode:</h4>"
                filehandle = t[0]
                print "<pre>"
                for i in filehandle:
                    sys.stdout.write( i )
                print "</pre>"
            except Exception, e:
                print "Can't read Source:", e


    #_______________________________________________________________________
    # Informations-Methoden

    def session_data( self ):
        """ Session Informationen anzeigen """
        self.menu()
        print "<hr>"

        print "<h3>session data</h3>"
        print '<table id="internals_session_data" class="internals_table">'
        for k,v in self.session.iteritems():
            print "<tr>"
            print "<td>%s</td>" % k
            print "<td>: %s</td>" % v
            #~ print "%s:%s\n" % (k,v)
            print "</tr>"

        #~ result = self.db.select(
                #~ select_items    = ["session_data"],
                #~ from_table      = "session_data",
                #~ where           = [("session_id",self.session.ID)]
            #~ )
        #~ for line in result:
            #~ print str( line ).replace("\\n","<br/>")

        print "<tr><td>config.system.poormans_modrewrite</td>"
        print "<td>: %s</td></tr>" % self.config.system.poormans_modrewrite

        print "<tr><td>config.system.page_ident</td>"
        print "<td>: '%s'</td></tr>" % self.config.system.page_ident

        print "<tr><td>config.system.script_filename</td>"
        print "<td>: '%s'</td></tr>" % self.config.system.script_filename

        print "<tr><td>config.system.document_root</td>"
        print "<td>: '%s'</td></tr>" % self.config.system.document_root

        print "<tr><td>config.system.real_self_url</td>"
        print "<td>: '%s'</td></tr>" % self.config.system.real_self_url

        print "<tr><td>config.system.poormans_url</td>"
        print "<td>: '%s'</td></tr>" % self.config.system.poormans_url

        print "</table>"

    #_______________________________________________________________________

    def system_info( self ):
        """ Allgemeine System Informationen """
        self.menu()
        print "<hr>"

        print "<h3>system info</h3>"

        def cmd_info( info, command, cwd="/" ):
            print "<p>%s:</p>" % info
            try:
                process = self.tools.subprocess2( command, cwd, 1 )
            except Exception,e:
                print "Can't get: %s" % e
            else:
                print "<pre>%s</pre>" % process.out_data.replace("\n","<br />")

        print '<dl id="system_info">'
        if hasattr(os,"uname"): # Nicht unter Windows verfügbar
            print "<dt>os.uname():</dt>"
            print "<dd>%s</dd>" % " - ".join( os.uname() )

        print "<dt>sys.version:</dt>"
        print "<dd>Python v%s</dd>" % sys.version

        print "<dt>sys.path:</dt>"
        for i in sys.path:
            print "<dd>%s</dd>" % i

        print "<dt>config file:</dt>"
        print "<dd>%s</dd>" % self.config.__file__

        import locale

        print "<dt>locale.getlocale():</dt>"
        print "<dd>%s</dd>" % str( locale.getlocale() )
        print "<dt>locale.getdefaultlocale():</dt>"
        print "<dd>%s</dd>" % str( locale.getdefaultlocale() )
        print "<dt>locale.getpreferredencoding():</dt>"
        try:
            print "<dd>%s</dd>" % str( locale.getpreferredencoding() )
        except Exception, e:
            print "<dd>Error: %s</dd>" % e

        print "</dl>"

        cmd_info( "uptime", "uptime" )
        cmd_info( "lokal Angemeldete Benutzer", "who -H -u --lookup" )
        cmd_info( "disk", "df -T -h" )
        cmd_info( "RAM", "free -m" )

        print "<h3>OS-Enviroment:</h3>"
        print '<dl id="environment">'
        keys = os.environ.keys()
        keys.sort()
        for key in keys:
            value = os.environ[key]
            print "<dt>%s</dt>" % key
            print "<dd>%s</dd>" % value
        print "</dl>"

    #_______________________________________________________________________

    def sql_status( self ):
        self.menu()
        print "<hr>"

        print "<h3>SQL table status</h3>"

        SQLresult = self.db.fetchall( "SHOW TABLE STATUS" )

        print '<table id="internals_log_information" class="internals_table">'

        # Tabellen überschriften generieren
        print "<tr>"
        print "<th>name</th>"
        print "<th>entries</th>" # Rows
        print "<th>update_time</th>"
        print "<th>size</th>"
        print "<th>overhang</th>" # data_free
        print "<th>collation</th>"
        print "</tr>"

        total_rows = 0
        total_size = 0
        total_data_free = 0
        # eigentlichen Tabellen Daten erzeugen
        for line in SQLresult:
            print "<tr>"
            print "<td>%s</td>" % line["Name"]

            print '<td style="text-align: right;">%s</td>' % line["Rows"]
            total_rows += line["Rows"]

            print "<td>%s</td>" % line["Update_time"]

            size = line["Data_length"] + line["Index_length"]
            print '<td style="text-align: right;">%sKB</td>' % self.tools.formatter( size/1024.0, "%0.1f")
            total_size += size

            if line["Data_free"]>0:
                data_free_size = "%sBytes" % self.tools.formatter( line["Data_free"], "%i" )
            else:
                data_free_size = '-'
            print '<td style="text-align: center;">%s</td>' % data_free_size
            total_data_free += line["Data_free"]

            print "<td>%s</td>" % line["Collation"]
            #~ print "<td>%s</td>" % line["Comment"]
            print "</tr>"

        print '<tr style="font-weight:bold">'
        print "<td></td>"
        print '<td style="text-align: right;">%s</td>' % total_rows
        print "<td></td>"
        print '<td style="text-align: right;">%sKB</td>' % self.tools.formatter( total_size/1024.0, "%0.1f")
        print '<td style="text-align: center;">%sBytes</td>' % self.tools.formatter( total_data_free, "%i" )
        print "<td></td>"
        print "</tr>"

        print "</table>"

        print '<p><a href="%soptimize_sql_tables">optimize SQL tables</a></p>' % self.URLs["action"]


    #_______________________________________________________________________
    # Log Daten

    def log_data( self ):
        """ Logging Informationen anzeigen """
        self.menu()
        print "<hr>"

        limit = 100 # Anzahl der Einträge die angezeigt werden sollen

        result = self.db.select(
            select_items    = ["timestamp", "sid", "user_name", "domain", "message","typ","status"],
            from_table      = "log",
            order           = ("timestamp","DESC"),
            limit           = (0,limit)
        )


        print "<h3>log information (last %i)</h3>" % limit
        print self.make_table_from_sql_select(
            result,
            id          = "internals_log_data",
            css_class   = "internals_table"
        )

    def make_table_from_sql_select( self, select_results, id, css_class ):
        """ Allgemeine Information um SQL-SELECT Ergebnisse als Tabelle zu erhalten """
        print '<table id="%s" class="%s">' % (id,css_class)

        # Tabellen überschriften generieren
        print "<tr>"
        for key in select_results[0].keys():
            print "<th>%s</th>" % key
        print "</tr>"

        # eigentlichen Tabellen Daten erzeugen
        for line in select_results:
            print "<tr>"
            for value in line.values():
                print "<td>%s</td>" % value
            print "</tr>"

        print "</table>"

    #_______________________________________________________________________
    # Funktionen

    def optimize_sql_tables( self ):

        SQLresult = self.db.fetchall( "SHOW TABLE STATUS" )

        # Tabellen mit Überhang rausfiltern
        tables_to_optimize = []
        for line in SQLresult:
            if line["Data_free"]>0:
                # Tabelle hat Überhang
                tables_to_optimize.append( line["Name"] )

        if len(tables_to_optimize) > 0:
            print "<h3>optimize SQL tables</h3>"

            tables_to_optimize = ",".join( tables_to_optimize )

            SQLresult = self.db.fetchall( "OPTIMIZE TABLE %s" % tables_to_optimize )

            print '<table id="optimize_table" class="internals_table">'

            # Überschriften
            print "<tr>"
            for desc in SQLresult[0].keys():
                print "<th>%s</th>" % desc
            print "</tr>"

            # Ergebniss Werte auflisten
            for line in SQLresult:
                print '<tr style="text-align: center;">'
                for value in line.values():
                    print "<td>%s</td>" % value
                print "</tr>"

            print "</table>"
        else:
            self.page_msg( "All Tables already up to date." )

        self.sql_status()




#_______________________________________________________________________
# Python Module-Info


class modules_info:
    """
    Auflisten aller installierten Module
    """
    def __init__( self ):
        self.glob_suffixes = self.get_suffixes()

        filelist = self.scan()
        self.modulelist = self.test( filelist )

    def get_suffixes( self ):
        """
        Liste aller Endungen aufbereitet für glob()
        """
        suffixes = ["*"+i[0] for i in imp.get_suffixes()]
        suffixes = "[%s]" % "|".join(suffixes)
        return suffixes

    def get_files( self, path ):
        """
        Liefert alle potentiellen Modul-Dateien eines Verzeichnisses
        """
        files = []
        for suffix in self.glob_suffixes:
            searchstring = os.path.join( path, suffix )
            files += glob.glob(searchstring)
        return files

    def scan( self ):
        """
        Verzeichnisse nach Modulen abscannen
        """
        filelist = []
        pathlist = sys.path
        for path_item in pathlist:
            if not os.path.isdir( path_item ):
                continue

            for file in self.get_files( path_item ):
                file = os.path.split( file )[1]
                if file == "__init__.py":
                    continue

                filename = os.path.splitext( file )[0]

                if filename in filelist:
                    continue
                else:
                    filelist.append( filename )

        return filelist

    def test( self, filelist ):
        """
        Testet ob alle gefunden Dateien auch als Modul
        importiert werden können
        """
        modulelist = []
        for filename in filelist:
            if filename == "": continue
            try:
                imp.find_module( filename )
            except:
                continue
            modulelist.append( filename )
        return modulelist

