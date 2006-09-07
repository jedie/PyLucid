#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Administration Sub-Menü : "show internals"
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.2.1"

__history__="""
v0.2.1
    - colubrid debug-Informationen werden nun in einem Fenster angezeigt
v0.2
    - NEU: system info "PyLucid environ information"
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
    - Auf self.response.write(Ausgaben halb umgestellt)
v0.0.4
    - Andere Handhabung von tools
v0.0.3
    - verweinfachung in SQL_table_status() und optimize_sql_table() durch
        MySQLdb.cursors.DictCursor
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



from PyLucid.system.BaseModule import PyLucidBaseModule

class show_internals(PyLucidBaseModule):
    def link( self ):
        return '<a href="%smenu">show_internals</a>' % self.URLs["action"]

    #_______________________________________________________________________

    def menu( self ):
        self.response.write(
            "<h4>show internals v%s</h4>" % __version__
        )
        self.response.write(self.module_manager.build_menu())

    #_______________________________________________________________________

    def python_modules( self ):
        self.response.write("<h3>Python Module Info</h3>")

        start_time = time.time()
        modulelist = modules_info().modulelist
        duration_time = time.time() - start_time

        self.response.write(
            "%s Modules found in %.2fsec.:" % (len(modulelist), duration_time)
        )
        self.response.write('<table>')
        Link = '<a href="%s' % self.URLs["action"]
        Link += '%s">more Info</a>'

        modulelist.sort()
        for modulename in modulelist:
            #~ if modei
            self.response.write("<tr>")
            self.response.write("<td>%s</td>" % modulename)
            self.response.write(
                '<td><a href="%smodule_info&modulename=%s">more info</a></td>' % (
                    self.URLs["action"], modulename
                )
            )
            self.response.write("</tr>")
        self.response.write("</table>")

    def module_info( self ):
        back_link = '<a href="%spython_modules">back</a>' % self.URLs["action"]
        self.response.write(back_link)
        try:
            module_name = self.request.args["modulename"]
        except KeyError, e:
            self.response.write("Error:", e)
            return

        self.response.write("<h3>Modul info: '%s'</h3>" % module_name)

        try:
            t = imp.find_module( module_name )
        except Exception,e:
            self.response.write("Can't import '%s':" % module_name)
            self.response.write(e)
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

        self.response.write(back_link)
        self.response.write("<ul>")
        self.response.write("<li>pathname: %s</li>" % t[1])
        self.response.write("<li>description: %s</li>" % str(t[2]))
        self.response.write("<li>fileinfo: %s</li>" % fileinfo)
        self.response.write("</ul>")

        try:
            module = __import__( module_name )
        except Exception,e:
            self.response.write("<p>Can't import module ;(</p>")
            return
        else:
            self.response.write("<h4>help:</h4>")
            self.response.write("<pre>")
            help( module )
            self.response.write("</pre>")

        if t[2][1] == "rb":
            self.response.write("<p>(SourceCode not available. It's a binary module.)</p>")
        else:
            try:
                self.response.write("<h4>SourceCode:</h4>")
                filehandle = t[0]
                self.response.write("<pre>")
                for i in filehandle:
                    sys.stdout.write( i )
                self.response.write("</pre>")
            except Exception, e:
                self.response.write("Can't read Source:", e)


    #_______________________________________________________________________
    # Informations-Methoden

    def session_data( self ):
        """ Session Informationen anzeigen """
        self.menu()
        self.response.write("<hr>")

        self.response.write("<h3>session data</h3>")
        self.response.write('<fieldset id="system_info"><legend>your session data:</legend>')
        self.response.write('<table id="internals_session_data" class="internals_table">')
        for k,v in self.session.iteritems():
            self.response.write("<tr>")
            self.response.write("<td>%s</td>" % k)
            self.response.write("<td>: %s</td>" % v)
            #~ self.response.write("%s:%s\n" % (k,v))
            self.response.write("</tr>")

        #~ result = self.db.select(
                #~ select_items    = ["session_data"],
                #~ from_table      = "session_data",
                #~ where           = [("session_id",self.session["session_id"])]
                #~ limit           = 10
            #~ )
        #~ for line in result:
            #~ self.response.write(str( line ).replace("\\n","<br/>"))

        self.response.write("</table>")
        self.response.write("</fieldset>")

    #_______________________________________________________________________

    def system_info( self ):
        """ Allgemeine System Informationen """
        self.menu()
        s = system_info(self.request, self.response)
        s.display_all()

    def colubrid_debug(self):
        self.response.startFreshResponse()

        self.response.write("<h3>Colubrid debug information</h3>")
        self.response.write('<fieldset id="system_info"><legend>colubrid:</legend>')
        try:
            from colubrid.debug import debug_info
            self.response.write(debug_info(self.request))
        except Exception, e:
            self.response.write("(Error: %s)" % e)
        self.response.write("</fieldset>")

        return self.response

    #_______________________________________________________________________

    def sql_status( self ):
        self.menu()
        self.response.write("<hr>")

        self.response.write("<h3>SQL table status</h3>")

        SQLresult = self.db.process_statement("SHOW TABLE STATUS")

        self.response.write(
            '<table id="internals_log_information" class="internals_table">'
        )

        # Tabellen überschriften generieren
        self.response.write("<tr>")
        self.response.write("<th>name</th>")
        self.response.write("<th>entries</th>") # Rows)
        self.response.write("<th>update_time</th>")
        self.response.write("<th>size</th>")
        self.response.write("<th>overhang</th>") # data_free)
        self.response.write("<th>collation</th>")
        self.response.write("</tr>")

        total_rows = 0
        total_size = 0
        total_data_free = 0
        # eigentlichen Tabellen Daten erzeugen
        for line in SQLresult:
            self.response.write("<tr>")
            self.response.write("<td>%s</td>" % line["Name"])

            self.response.write(
                '<td style="text-align: right;">%s</td>' % line["Rows"]
            )
            total_rows += line["Rows"]

            self.response.write("<td>%s</td>" % line["Update_time"])

            size = line["Data_length"] + line["Index_length"]
            self.response.write(
                '<td style="text-align: right;">%sKB</td>' % \
                    self.tools.formatter( size/1024.0, "%0.1f")
            )
            total_size += size

            if line["Data_free"]>0:
                data_free_size = "%sBytes" % \
                    self.tools.formatter(line["Data_free"], "%i")
            else:
                data_free_size = '-'
            self.response.write(
                '<td style="text-align: center;">%s</td>' % data_free_size
            )
            total_data_free += line["Data_free"]

            self.response.write("<td>%s</td>" % line["Collation"])
            #~ self.response.write("<td>%s</td>" % line["Comment"])
            self.response.write("</tr>")

        self.response.write('<tr style="font-weight:bold">')
        self.response.write("<td></td>")
        self.response.write('<td style="text-align: right;">%s</td>' % total_rows)
        self.response.write("<td></td>")
        self.response.write(
            '<td style="text-align: right;">%sKB</td>' % \
                self.tools.formatter( total_size/1024.0, "%0.1f")
        )
        self.response.write(
            '<td style="text-align: center;">%sBytes</td>' % \
                self.tools.formatter( total_data_free, "%i" )
        )
        self.response.write("<td></td>")
        self.response.write("</tr>")

        self.response.write("</table>")

        self.response.write(
            '<p><a href="%s">optimize SQL tables</a></p>' % \
                self.URLs.make_action_link("optimize_sql_tables")
        )


    #_______________________________________________________________________
    # Log Daten

    def log_data( self ):
        """ Logging Informationen anzeigen """
        self.menu()
        self.response.write("<hr>")

        limit = 100 # Anzahl der Einträge die angezeigt werden sollen

        result = self.db.get_last_logs(limit)

        self.response.write("<h3>log information (last %i)</h3>" % limit)
        self.response.write(
            self.tools.make_table_from_sql_select(
                result,
                id          = "internals_log_data",
                css_class   = "internals_table"
            )
        )



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
            self.response.write("<h3>optimize SQL tables</h3>")

            tables_to_optimize = ",".join( tables_to_optimize )

            SQLresult = self.db.fetchall( "OPTIMIZE TABLE %s" % tables_to_optimize )

            self.response.write('<table id="optimize_table" class="internals_table">')

            # Überschriften
            self.response.write("<tr>")
            for desc in SQLresult[0].keys():
                self.response.write("<th>%s</th>" % desc)
            self.response.write("</tr>")

            # Ergebniss Werte auflisten
            for line in SQLresult:
                self.response.write('<tr style="text-align: center;">')
                for value in line.values():
                    self.response.write("<td>%s</td>" % value)
                self.response.write("</tr>")

            self.response.write("</table>")
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




class system_info(PyLucidBaseModule):
    def display_all(self):
        self.response.write("<hr>")

        self.PyLucid_info()
        self.system_info()
        self.encoding_info()
        self.envion_info()
        self.colubrid_debug_link()

    #_________________________________________________________________________

    def PyLucid_info(self):
        self.response.write("<h3>PyLucid environ information</h3>")
        self.response.write('<fieldset id="system_info"><legend>PyLucid["URLs"]:</legend>')
        self.response.write("<pre>")
        for k,v in self.URLs.items():
            self.response.write("%15s: '%s'\n" % (k,v))
        self.response.write("</pre>")
        self.response.write("</fieldset>")

    #_________________________________________________________________________

    def system_info(self):
        self.response.write("<h3>system info</h3>")

        self.response.write('<dl id="system_info">')
        if hasattr(os,"uname"): # Nicht unter Windows verfügbar
            self.response.write("<dt>os.uname():</dt>")
            self.response.write("<dd>%s</dd>" % " - ".join( os.uname() ))

        self.response.write("<dt>sys.version:</dt>")
        self.response.write("<dd>Python v%s</dd>" % sys.version)

        self.response.write("<dt>sys.path:</dt>")
        for i in sys.path:
            self.response.write("<dd>%s</dd>" % i)

        #~ self.response.write("<dt>config file:</dt>")
        #~ self.response.write("<dd>%s</dd>" % self.config.__file__)

        self.response.write("</dl>")

        #_____________________________________________________________________

        self.cmd_info( "uptime", "uptime" )
        self.cmd_info( "lokal Angemeldete Benutzer", "who -H -u --lookup" )
        self.cmd_info( "disk", "df -T -h" )
        self.cmd_info( "RAM", "free -m" )

    #_________________________________________________________________________

    def envion_info(self):
        self.response.write("<h3>OS-Enviroment:</h3>")
        self.response.write('<dl id="environment">')
        keys = os.environ.keys()
        keys.sort()
        for key in keys:
            value = os.environ[key]
            self.response.write("<dt>%s</dt>" % key)
            self.response.write("<dd>%s</dd>" % value)
        self.response.write("</dl>")

    def colubrid_debug_link(self):
        self.response.write("<h3>Colubrid debug information</h3>")
        # FIXME: Das JS sollte anders eingebunden werden!
        url = self.URLs.actionLink("colubrid_debug")
        self.response.write(
            '<script type="text/javascript">'
            '/* <![CDATA[ */'
            'function OpenInWindow(URL) {'
            '  win1 = window.open('
            'URL, "", "width=1000, height=600, dependent=yes, resizable=yes,'
            ' scrollbars=yes, location=no, menubar=no, status=no,'
            ' toolbar=no");'
            '  win1.focus();'
            '}'
            '/* ]]> */'
            '</script>'
        )
        html = (
            '<a href="%s" onclick="OpenInWindow(this.href); return false"'
            ' title="colubrid debug">'
            'show colubrid debug'
            '</a>'
        ) % url
        self.response.write(html)

    #_________________________________________________________________________

    def encoding_info(self):
        self.response.write("<h3>encoding info</h3>")
        import locale

        self.response.write('<dl id="system_info">')

        def get_file_encoding(f):
            if hasattr(f, "encoding"):
                return f.encoding
            else:
                return "Error: Object has no .encoding!"

        self.response.write("<dt>sys.stdin.encoding:</dt>")
        self.response.write("<dd>%s</dd>" % get_file_encoding(sys.stdin))

        self.response.write("<dt>sys.stdout.encoding:</dt>")
        self.response.write("<dd>%s</dd>" % get_file_encoding(sys.stdout))

        self.response.write("<dt>sys.stderr.encoding:</dt>")
        self.response.write("<dd>%s</dd>" % get_file_encoding(sys.stderr))


        self.response.write("<dt>sys.getdefaultencoding():</dt>")
        self.response.write("<dd>%s</dd>" % sys.getdefaultencoding())

        self.response.write("<dt>sys.getfilesystemencoding():</dt>")
        try:
            self.response.write("<dd>%s</dd>" % sys.getfilesystemencoding())
        except Exception, e:
            self.response.write("<dd>Error: %s</dd>" % e)

        self.response.write("<dt>locale.getlocale():</dt>")
        self.response.write("<dd>%s</dd>" % str( locale.getlocale() ))

        self.response.write("<dt>locale.getdefaultlocale():</dt>")
        self.response.write("<dd>%s</dd>" % str( locale.getdefaultlocale() ))

        self.response.write("<dt>locale.getpreferredencoding():</dt>")
        try:
            self.response.write("<dd>%s</dd>" % str( locale.getpreferredencoding() ))
        except Exception, e:
            self.response.write("<dd>Error: %s</dd>" % e)

        self.response.write("</dl>")

    #_________________________________________________________________________

    def cmd_info(self, info, command, cwd="/"):
        self.response.write(
            '<fieldset id="system_info"><legend>%s:</legend>' % info
        )
        try:
            process = self.tools.subprocess2(command, cwd, 5)
        except Exception,e:
            self.response.write("Can't get: %s" % e)
        else:
            self.response.write("<pre>%s</pre>" % process.out_data)
        self.response.write("</fieldset>")








