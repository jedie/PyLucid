#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Erzeugt einen Download des MySQL Dumps
http://dev.mysql.com/doc/mysql/de/mysqldump.html

Last commit info:
----------------------------------
LastChangedDate: $LastChangedDate$
Revision.......: $Rev$
Author.........: $Author$
date...........: $Date$
"""

__version__ = "$Rev$"


__todo__ = """
    http://dev.mysql.com/doc/refman/4.1/en/show-create-table.html

    SHOW CREATE TABLE tbl_name
"""


import os, sys, cgi, time
import re, StringIO, zipfile

from colubrid import HttpResponse

from PyLucid.tools import formatter
from PyLucid.components.plugin_cfg import PluginConfig
from PyLucid.system.BaseModule import PyLucidBaseModule


class MySQLdump(PyLucidBaseModule):

    def __init__(self, request, response):
        super(MySQLdump, self).__init__(request, response)

        if sys.platform == "win32":
            self.mysqldump_name = "mysqldump.exe"
        else:
            self.mysqldump_name = "mysqldump"

        self.plugin_cfg = PluginConfig(self.request, self.response)

    def menu(self):
        """ Menü für Aktionen generieren """
        #~ self.URLs.debug()
        #~ self.response.debug()

        if "action" in self.request.form:
            actions = {
                "display_dump": self.display_dump,
                "display_command": self.display_command,
                "download_dump": self.download_dump,
                "install_dump": self.PyLucid_install_dump,
                "save_settings": self.save_settings,
            }
            actionKey = self.request.form["action"]
            try:
                action = actions[actionKey]
            except KeyError, e:
                self.response("Subaction '%s' unknown!")
                return

            try:
                response = action()
            except MysqldumpNotFound:
                self.response.write(
                    "<p>Please use the browser back button.</p>"
                )
                return
            except CreateDumpError:
                return
            else:
                return response

        self.display_menu()

    def display_menu(self):

        # Tabellen die per default nur die Struktur gespeichert werden soll
        default_no_data = ["log", "session_data"]
        default_no_data = [
            self.preferences["dbTablePrefix"] + i for i in default_no_data
        ]

        table_list = self.db.get_tables()
        table_data = []
        for table in table_list:
            table = {"name": table}
            if table["name"] in default_no_data:
                table["structure"] = True
            else:
                table["complete"] = True

            table_data.append(table)

        self.actions = [
            ("download_dump",   "download dump"),
            ("display_dump",    "display SQL dump"),
            ("install_dump",    "download PyLucid install dump"),
            ("display_command", "display mysqldump command"),
        ]

        try:
            mysqldump_path = self.get_mysqldump_path()
        except MysqldumpNotFound:
            mysqldump_path = ""

        context = {
            "version"               : __version__,
            "table_data"            : table_data,
            "path"                  : mysqldump_path,
            "url"                   : self.URLs.currentAction(),
            "server_version"        : self.db.RAWserver_version,
            "help_link"             : self.URLs.actionLink("display_help"),
            "actions"               : self.actions,
            "character_set"         : self.plugin_cfg["default character set"],
            "default_parameters"    : " ".join(self.plugin_cfg["default parameters"]),
            "parameter_examples"    : " ".join(self.plugin_cfg["parameter examples"]),
        }
        #~ self.page_msg(context)
        self.templates.write("Menu", context)

    def get_mysqldump_path(self):
        """
        Sucht das mysqldump Programm im Pfad. Wurde das Formular abgeschickt,
        wird darin
        """
        path_list = []

        try:
            path = os.environ["PATH"]
        except KeyError:
            self.page_msg("No 'PATH' in environ?!?")
            path_list = []
        else:
            path_list = path.split(os.pathsep)
            path_list = [d.strip('"') for d in path_list] # Windows
        #~ self.page_msg("path_list:", path_list)

        if "mysqldump_path" in self.request.form:
            # Das Formular wurde schon abgeschickt, dann schauen wir erst da
            # rein!
            form_path = self.request.form["mysqldump_path"]
            if os.path.isdir(form_path):
                path_list.insert(0, form_path)
            else:
                self.page_msg("mysqldump path not exists! Ignored.")

        if "mysqldump_path" in self.plugin_cfg:
            # In der plugin_cfg ist der Pfad auch schon mal gespeichert.
            path_list.insert(0, self.plugin_cfg["mysqldump_path"])

        for test_path in path_list:
            if os.path.isfile(os.path.join(test_path, self.mysqldump_name)):
                # gefunden!
                return test_path

        self.page_msg(
            "Note: mysqldump program not found!"
            " Please put the correct path in the html form."
        )
        raise MysqldumpNotFound()

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
        dumpLen = formatter.filesizeformat(dumpLen)
        msg = (
            "<p><small>"
            "(mysqldump duration %.2f sec. - size: %s)"
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
        self.plugin_cfg = self.plugin_cfg

        command_list = ["%s --help" % self.mysqldump_name]

        self.response.write("<p>command: '%s'</p>" % command_list[0])

        output = self._run_command_list(command_list, timeout = 2)
        if output == False:
            # Fehler aufgereten
            return

        self.response.write("<pre>%s</pre>" % output)

    #_______________________________________________________________________

    def display_command( self ):
        """
        mysqldump Kommandos anzeigen, je nach Formular-Angaben
        """

        mysqldump_path = self.request.form["mysqldump_path"]
        self.response.write("<h3>Display command only:</h3>")
        self.response.write("<pre>")
        for command in self._get_sql_commands():
            command = self._cleanup_sql_command(command)
            self.response.write("%s>%s\n" % (mysqldump_path, command))
        self.response.write("</pre>")
        self.response.write('<a href="JavaScript:history.back();">back</a>')


    def _cleanup_sql_command(self, command):
        """
        Löschen des Passwortes aus dem Kommando, damit man es in den Dump
        einbauen kann
        """
        if self.preferences["dbPassword"].strip() == "":
            # Es gibt kein Passwort, was gelöscht werden kann ;)
            return command
        else:
            return command.replace(self.preferences["dbPassword"],"***")


    def _get_sql_commands( self ):
        """
        Erstellt die Kommandoliste anhand der CGI-Daten bzw. des Formulars ;)
        """
        def get_option(form_key, format_string):
            value = self.request.form.get(form_key, "")
            value = value.strip()
            if value != "":
                value = format_string % value
            return value

        options         = get_option("options", " %s")
        compatible      = get_option("compatible", " --compatible=%s")
        character_set   = get_option(
            "character-set", " --default-character-set=%s"
        )

        default_command = (
            "%(fn)s%(cs)s%(cp)s%(op)s"
            " -h%(h)s %(n)s -u%(u)s"
        ) % {
            "fn" : self.mysqldump_name,
            "cs" : character_set,
            "cp" : compatible,
            "op" : options,
            "u"  : self.preferences["dbUserName"],
            "h"  : self.preferences["dbHost"],
            "n"  : self.preferences["dbDatabaseName"],
        }

        if self.preferences["dbPassword"].strip() != "":
            # Es gibt ein Passwort
            default_command += " -p%s" % self.preferences["dbPassword"]

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
        mysqldump_path = self.get_mysqldump_path()
        if not mysqldump_path:
            self.page_msg("Error!")
            return

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

    #_________________________________________________________________________

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
            cmd = self._cleanup_sql_command(cmd)
            txt += "-- %s\n" % cmd

        txt += "--\n"
        txt += "-- This file should be encoded in utf8 !\n"
        txt += "-- "
        txt += "-"*79
        txt += "\n"

        return txt

    #_______________________________________________________________________
    def save_settings(self):
        #~ self.response.debug()
        #~ self.page_msg(self.request.form)

        new = self.request.form.get('character-set', "")
        if new != self.plugin_cfg["default character set"]:
            self.plugin_cfg["default character set"] = new
            self.page_msg("Set default character set to: '%s'" % new)

        new = self.request.form.get("mysqldump_path", "")
        if new != self.plugin_cfg.get("mysqldump_path", ""):
            self.plugin_cfg["mysqldump_path"] = new
            self.page_msg("Set default mysqldump path to: '%s'" % new)

        options = self.request.form.get('options', None)
        if options:
            options = options.split(" ")
            for option in options:
                if not option in self.plugin_cfg['parameter examples']:
                    self.page_msg("Put option '%s' in the examples." % option)
                    self.plugin_cfg['parameter examples'].append(option)

            self.plugin_cfg['default parameters'] = options

        self.page_msg.green("Options saved for the next time ;)")

        self.display_menu()



class CreateDumpError(Exception):
    """
    Beim erstellen des Dumps ist irgendwas schief gelaufen
    """
    pass

class MysqldumpNotFound(Exception):
    """
    Das mysqldump Programm wurde nicht gefunden.
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

            if not category in outdata:
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