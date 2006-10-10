#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Erzeugt einen Download des MySQL Dumps
http://dev.mysql.com/doc/mysql/de/mysqldump.html
"""

__version__="0.4.2"

__history__="""
v0.4.2
    - Bugfixes, now it realy works under Windows too
v0.4.1
    - Nutzt nun response.startFileResponse() (s. sendFile()-Methode)
v0.4
    - Anpassung an PyLucid v0.7
v0.3.2
    - Quick hack to display mysql version informations
v0.3.1
    - Bugfix: options kann nun auch leer sein
v0.3
    - Anpassung an neuen ModuleManager, auslagern der Config.
v0.2.2
    - Nutzt die module_manager Einstelung "sys_exit", damit der Dumpdownload
        richtig beendet wird
    - In additional_dump_info ist in sys.version ein \n Zeichen, welches nun
        rausfliegt.
v0.2.1
    - Anpassung an self.db.print_internal_page()
v0.2.0
    - HTML-Ausgaben nun über interne Seite
v0.1.2
    - Umbenennung in MySQLdump, weil's ja nur für MySQL geht...
    - NEU: Nun kann man auch den Pfad zu mysqldump angeben.
        Standard ist "." (aktuelles Verzeichnis) damit wird mysqldump im Pfad
        gesucht. Das klappt nun auch unter Windows
v0.1.1
    - NEU: Man kann nun genau auswählen was von welcher Tabelle man haben will
v0.1.0
    - Anpassung an Module-Manager
    - Umau an einigen Stellen
v0.0.4
    - Es ist nun möglich kein "--compatible=" Parameter zu benutzen
        (wichtig bei MySQL server <v4.1.0)
v0.0.3
    - Module-Manager Angabe "direct_out" hinzugefügt, damit der Download des
      Dumps auch funktioniert.
v0.0.2
    - Großer Umbau: Anderes Menü, anderer Aufruf von mysqldump, Möglichkeiten
        Dump-Parameter anzugeben
v0.0.1
    - Erste Version
"""

__todo__ = """
    Using jinja!!!

    http://dev.mysql.com/doc/refman/4.1/en/show-create-table.html

    SHOW CREATE TABLE tbl_name

"""


import os, sys, cgi, time
import re, StringIO, zipfile

from colubrid import HttpResponse



from PyLucid.system.BaseModule import PyLucidBaseModule


class MySQLdump(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(MySQLdump, self).__init__(*args, **kwargs)

        if sys.platform == "win32":
            self.mysqldump_name = "mysqldump.exe"
        else:
            self.mysqldump_name = "mysqldump"

    def menu(self):
        """ Menü für Aktionen generieren """
        #~ self.URLs.debug()
        #~ self.response.debug()

        if self.request.form.get("action", False):
            actions = {
                "display_help": self.display_help,
                "display_dump": self.display_dump,
                "display_command": self.display_command,
                "download_dump": self.download_dump,
                "install_dump": self.PyLucid_install_dump,
            }
            actionKey = self.request.form["action"]
            try:
                action = actions[actionKey]
            except KeyError, e:
                self.response("Subaction '%s' unknown!")
                return

            try:
                response = action()
            except CreateDumpError:
                return
            else:
                return response

        default_no_data = ["log", "session_data"]
        default_no_data = [
            self.preferences["dbTablePrefix"] + i for i in default_no_data
        ]

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
            ("download_dump",   "download dump"),
            ("display_dump",    "display SQL dump"),
            ("install_dump",    "download PyLucid install dump"),
            ("display_help",    "mysqldump help" ),
            ("display_command", "display mysqldump command"),
        ]

        buttons = (
            "<p>Your mysql server version: <em>v%s</em></p>"
        ) % self.db.RAWserver_version

        for action in self.actions:
            buttons += (
                '<button type="submit" name="action" value="%s">'
                '%s</button>&nbsp;&nbsp;\n'
            ) % (action[0], action[1])

        #~ raw_downloads = [
            #~ ("url1", "title1"),
            #~ ("url2", "title2"),
        #~ ]
        context = {
            "version"       : __version__,
            "tables"        : table_data,
            "path"          : self.get_mysqldump_path(),
            "url"           : self.URLs.currentAction(),
            "buttons"       : buttons,
            "character_set" : "utf8",#self.db.encoding,
        }

        self.templates.write("Menu", context)

    def get_mysqldump_path(self):
        if not "PATH" in os.environ:
            return "[ERROR: No 'PATH' in environ!]"

        path = os.environ["PATH"]
        if path.find(";")!=-1:
            # Unter Windows wird mit : getrennt
            path = path.replace(";", ":")

        path_list = path.split(":")

        for test_path in path_list:
            if os.path.isfile(os.path.join(test_path, self.mysqldump_name)):
                return test_path

        return "[ERROR: '%s' not found in PATH!]" % (self.mysqldump_name)



    #_______________________________________________________________________

    def sendFile(self, content, filename):
        """
        Startet den Download der Datei zum Browser
        """
        content_len = len(content)
        self.response.startFileResponse(filename, content_len)
        self.response.write(content)
        return self.response

    #_______________________________________________________________________

    def download_dump(self):
        """
        Erstellt den SQL Dump und bietet diesen direk zum Download an
        """
        #~ self.page_msg("download dump!")

        dump, filename = self.makedump()

        # Datei zum Browser senden
        return self.sendFile(dump, filename)


    def PyLucid_install_dump(self):
        dump, dumpfilename = self.makedump()

        dbTablePrefix = self.preferences["dbTablePrefix"]
        dump = universalize_dump(self.response, dbTablePrefix).process(dump)

        buffer = StringIO.StringIO()
        z = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)

        for filename,data in dump.iteritems():
            filename = filename.encode("UTF8")
            data = data.encode("UTF8")
            z.writestr(filename,data)
        z.close()

        buffer.seek(0) # An den Anfang der ZIP Datei springen

        content = buffer.read()
        filename = "%s.zip" % dumpfilename

        # Debug:
        #~ self.response.write("<pre>\n")
        #~ self.response.write("Keys: %s\n" % dump.keys())
        #~ for k,v in dump.iteritems():
            #~ self.response.write("<strong>%s</strong>\n" % k)
            #~ self.response.write("%s\n" % cgi.escape(v))
        #~ self.response.write("\nfilename: %s\n" % filename)
        #~ self.response.write("\nZIP file len: %s\n" % len(content))
        #~ self.response.write(
            #~ "\nZIP content: %s...\n" % cgi.escape(content[:50])
        #~ )
        #~ self.response.write("</pre>\n")
        #~ return

        # Datei zum Browser senden
        return self.sendFile(content, filename)


    #_______________________________________________________________________

    def display_dump(self):
        """
        Zeigt den SQL dump im Browser an
        """
        start_time = time.time()
        dump, filename = self.makedump()

        dumpLen = len(dump)
        dumpLen = self.tools.formatter(dumpLen, format="%0i")
        msg = (
            "<p><small>"
            "(mysqldump duration %.2f sec. - size: %s Bytes)"
            "</small></p>"
        ) % (
            (time.time() - start_time), dumpLen
        )
        self.response.write(msg)

        self.response.write("<pre>%s</pre>" % cgi.escape(dump))

        self.response.write('<a href="JavaScript:history.back();">back</a>')

    #_______________________________________________________________________

    def display_help( self ):
        """
        Zeigt die Hilfe von mysqldump an
        """
        command_list = ["%s --help" % self.mysqldump_name]

        self.response.write('<p><a href="JavaScript:history.back();">back</a></p>')

        self.response.write("<p>command: '%s'</p>" % command_list[0])

        output = self._run_command_list(command_list, timeout = 2)
        if output == False:
            # Fehler aufgereten
            return

        self.response.write("<pre>%s</pre>" % output)

        self.response.write('<a href="JavaScript:history.back();">back</a>')

    #_______________________________________________________________________

    def display_command( self ):
        """
        mysqldump Kommandos anzeigen, je nach Formular-Angaben
        """

        mysqldump_path = self.request.form["mysqldump_path"]
        self.response.write("<h3>Display command only:</h3>")
        self.response.write("<pre>")
        for command in self._get_sql_commands():
            self.response.write(
                "%s>%s" % (
                    mysqldump_path,
                    command.replace(self.preferences["dbPassword"],"***")
                )
            )
        self.response.write("</pre>")
        self.response.write('<a href="JavaScript:history.back();">back</a>')


    def _get_sql_commands( self ):
        """
        Erstellt die Kommandoliste anhand der CGI-Daten bzw. des Formulars ;)
        """
        try:
            options = self.request.form["options"]
        except KeyError:
            options = ""
        else:
            options = " %s" % options

        try:
            compatible = self.request.form["compatible"]
        except KeyError:
            compatible = ""
        else:
            compatible = " --compatible=%s" % compatible

        default_command = (
            "%(fn)s --default-character-set=%(cs)s%(cp)s%(op)s"
            " -u%(u)s -p%(p)s -h%(h)s %(n)s"
        ) % {
            "fn" : self.mysqldump_name,
            "cs" : self.request.form["character-set"],
            "cp" : compatible,
            "op" : options,
            "u"  : self.preferences["dbUserName"],
            "p"  : self.preferences["dbPassword"],
            "h"  : self.preferences["dbHost"],
            "n"  : self.preferences["dbDatabaseName"],
        }

        tablenames = self.db.get_tables()
        structure_tables = []
        complete_tables = []
        for table in tablenames:
            dump_typ = self.request.form[table]

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

    #_______________________________________________________________________

    def makedump(self):
        command_list = self._get_sql_commands()
        dump = self._run_command_list(command_list, timeout = 120, header=True)

        # Zusatzinfo's in den Dump "einblenden"
        info = self.additional_dump_info()
        dump = info + dump

        filename = "%s_%s%s.sql" % (
            time.strftime("%Y%m%d"),
            self.preferences["dbTablePrefix"],
            self.preferences["dbDatabaseName"]
        )

        return dump, filename


    def _run_command_list(self, command_list, timeout, header=False):
        """
        Abarbeiten der >command_list<
        liefert die Ausgaben zurück oder erstellt direk eine Fehlermeldung
        """
        try:
            mysqldump_path = self.request.form["mysqldump_path"]
        except KeyError:
            # Wurde im Formular leer gelassen
            mysqldump_path = self.get_mysqldump_path("mysqldump")

        def print_error(out_data, returncode, msg):
            self.response.write("<h3>%s</h3>" % msg)
            self.response.write("<p>Returncode: %s<br />" % returncode)
            self.response.write(
                "output:<pre>%s</pre></p>" % cgi.escape( out_data )
            )

        result = u""
        for command in command_list:
            start_time = time.time()
            process = self.tools.subprocess2(command, mysqldump_path, timeout)
            out_data = process.out_data
            result += u"%s\n" % out_data

            if process.killed == True:
                print_error(
                    result, process.returncode,
                    "Error: subprocess timeout (%.2fsec.>%ssec.)" % (
                        time.time()-start_time, timeout
                    )
                )
                raise CreateDumpError
            if process.returncode != 0 and process.returncode != None:
                print_error(result, process.returncode, "subprocess Error!")
                raise CreateDumpError

        return result

    #_______________________________________________________________________

    def additional_dump_info(self):
        txt = u"-- "
        txt += "-"*79
        txt += "\n"

        txt += "-- Dump created %s with PyLucid's %s v%s\n" % (
            time.strftime("%d.%m.%Y, %H:%M"),
            os.path.split(__file__)[1], __version__
        )
        txt += "--\n"

        if hasattr(os,"uname"): # Nicht unter Windows verfügbar
            txt += "-- %s\n" % " - ".join(os.uname())

        txt += "-- Python v%s\n" % sys.version.replace("\n","")

        txt += "--\n"

        command_list = ["mysqldump --version"]
        output = self._run_command_list( command_list, timeout = 5 )
        if output != False:
            # kein Fehler aufgereten
            txt += "-- used:\n"
            txt += "-- %s\n" % output.replace("\n"," ")

        txt += "--\n"
        txt += "-- command list:\n"
        command_list = self._get_sql_commands()
        for cmd in command_list:
            txt += (
                "-- %s\n"
            ) % cmd.replace(self.preferences["dbPassword"],"***")

        txt += "--\n"
        txt += "-- This file should be encoded in utf8 !\n"
        txt += "-- "
        txt += "-"*79
        txt += "\n"

        return txt




class CreateDumpError(Exception):
    """
    Beim erstellen des Dumps ist irgendwas schief gelaufen
    """
    pass






# Einträge die rausfallen
filter_startswith = (
    "INSERT INTO `$$archive`",
    "INSERT INTO `$$log`",
    "INSERT INTO `$$md5users`",
    "INSERT INTO `$$pages_internal`",
    "INSERT INTO `$$plugindata`",
    "INSERT INTO `$$plugins`",
    "INSERT INTO `$$session_data`",
    "INSERT INTO `$$user_group`",

    "LOCK TABLES",
    "UNLOCK TABLES",
)

# Filter für zusätzliche SQL-Angaben im CREATE TABLE statement
pattern = "[^;, ]* *"
crate_table_filters = (
    "collate %s" % pattern,
    "ENGINE=%s" % pattern,
    "COLLATE=%s" % pattern,
    "character set %s" % pattern,
    "DEFAULT CHARSET=%s" % pattern,
    "TYPE=MyISAM(?<! COMMENT)" # (?<!\))
)

cleaning_filters = (
    "/\*.*?\*/;",
)

class universalize_dump:
    #FIXME: Völlig unnötig, wenn man eh die SQL-dump-Kommandos einzeln ausführen kann!!!
    def __init__(self, response, dbTablePrefix):
        self.response = response
        self.dbTablePrefix = dbTablePrefix

        self.in_create_table = False
        self.after_commend = False
        self.found_dbprefix = False


    def process(self, dumpData):
        """
        DUMP-Daten Konvertieren und in ZIP Datei schreiben
        """
        re_find_name = re.compile( r"`\$\$(.*?)`" )
        category = ""
        outdata = {}

        dumpData = dumpData.split("\n")
        #~ self.response.write(
            #~ "<pre>%s</pre>" % cgi.escape(
                #~ "<br />\n".join(dumpData)
            #~ )
        #~ )
        #~ sys.exit()

        for line in dumpData:
            line = self.preprocess(line)
            if line.startswith("--"):
                category = "info.txt"
            else:
                find_name = re_find_name.findall(line)
                if find_name != []:
                    category = find_name[0]+".sql"

            if not outdata.has_key(category):
                outdata[category] = ""

            if line=="": continue # Leere Zeilen brauchen wir nicht

            outdata[category] += line

        return outdata

        #~ if self.found_dbprefix == False:
            #~ self.response.write(
                #~ "ERROR: No table prefix '%s' found!!!" % self.dbTablePrefix
            #~ )


    def preprocess( self, line ):
        """
        -Filterung des aktuellen self.dbTablePrefix nach %(table_prefix)s
        -Einblendung der Dump-Informationen
        """
        # Prozentzeichen escapen
        prefix_mark = "`%s" % self.dbTablePrefix

        # Tabellen Prefixe ändern
        if line.find(prefix_mark)!=-1:
            self.found_dbprefix = True
            line = line.replace( prefix_mark, "`$$" )

        # Zeilen filtern
        for filter in filter_startswith:
            if line.startswith( filter ):
                return ""

        # Spezielle SQL Kommandos rausschmeißen
        #~ if line.startswith( "/*" ) and line.endswith( "*/;\n" ):
            #~ self.response.write(">", line)
            #~ return ""

        if line.startswith( "CREATE TABLE" ):
            self.in_create_table = True

        if self.in_create_table == True:
            #~ self.response.write(line[:-1])
            for filter in crate_table_filters:
                line = re.sub(filter, "", line)
            #~ self.response.write(">",line)
        else:
            line += "\n"

        if line.endswith(";"):
            line += "\n"
            self.in_create_table = False

        for filter in cleaning_filters:
            line = re.sub(filter, "", line)

        return line