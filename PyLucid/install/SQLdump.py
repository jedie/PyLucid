#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
SQL_dump Klasse zum "verwalten" des SQL-install-Dumps
"""


install_zipfileName = "PyLucid/PyLucid_SQL_install_data.zip"


debug = True
#~ debug = False


import os, sys, cgi, time, zipfile

try:
    import datetime
except ImportError:
    #FIXME: Besser time nehmen! datetime gibt es erst ab Python 2.3
    from PyLucid.python_backports import datetime






class SQLdump(object):
    """
    Klasse zum "verwalten" des SQL-install-Dumps
    """

    datetime_updates = {
        "styles": ("id", ["datetime", "lastupdatetime"]),
    }


    def __init__(self, request, response, simulation=False):
        self.response = response
        self.simulation = simulation

        # shorthands
        self.db = request.db
        self.tools = request.tools

        self.in_create_table = False
        self.in_insert = False

        self.newest_file_date = None

        try:
            self.ziparchiv = zipfile.ZipFile(install_zipfileName, "r")
        except (IOError, zipfile.BadZipfile), e:
            msg = (
                "<h2>Can't open install-file:</h2>\n"
                "<h4>%s - %s</h4>\n"
            ) % (sys.exc_info()[0], e)
            self.response.write(msg)
            sys.exit(1)

    def import_dump(self):
        table_names = self.get_table_names()
        self.response.write("<pre>")
        for current_table in table_names:
            self.response.write(
                "install DB table '<strong>%s</strong>'..." % current_table
            )
            if self.simulation:
                self.response.write("\n<code>\n")

            command = self.get_table_data(current_table)

            if debug:
                counter = self.execute_many(command)
            else:
                try:
                    counter = self.execute_many(command)
                except Exception,e:
                    self.response.write("<strong>ERROR: %s</strong>" % e)

            if self.simulation:
                self.response.write("</code>\n")
            else:
                self.response.write("OK\n")

        self.response.write("</pre>")

    #~ def setup_all_datetimes(self):
        #~ for table_name in tables:
            #~ self.setup_table_datetime(table_name)

    #~ def setup_table_datetime(self, table_name):
        #~ data = self.datetime_updates[table_name]
        #~ index_column, column_list = data

        #~ index_list = self.db.select(
            #~ select_items    = [index_column],
            #~ from_table      = table_name,
        #~ )
        #~ for index in index_list:
            #~ index = index[index_column]
            #~ print self.newest_file_date
            #~ print index
            #~ update_dict = {}
            #~ for column in column_list:
                #~ update_dict[column] = self.newest_file_date
            #~ print (index_column, index)
            #~ self.db.update(
                #~ table   = table_name,
                #~ data    = update_dict,
                #~ where   = (index_column, index)
            #~ )

    def install_tables(self, table_names):
        """ Installiert nur die Tabellen mit angegebenen Namen """
        self.response.write("<pre>")

        self.get_table_names()# FIXME: Damit self.newest_file_date gesetzt wird

        reinit_tables = list(table_names) # Kopie anlegen
        for current_table in table_names:
            msg = (
                "re-initialisation DB table '<strong>%s</strong>':\n"
            ) % current_table
            self.response.write(msg)
            command = self.get_table_data(current_table)

            self.response.write(" - Drop table...",)
            if self.simulation:
                self.response.write("\n<code>\n")
            try:
                status = self.execute("DROP TABLE $$%s;" % current_table)
            except Exception, e:
                self.response.write("Error: %s\n" % e)
            else:
                if self.simulation:
                    self.response.write("</code>\n")
                else:
                    self.response.write("OK\n")

            self.response.write(" - recreate Table and insert values...",)
            if self.simulation:
                self.response.write("\n<code>\n")
            #~ try:
            counter = self.execute_many(command)
            #~ except Exception,e:
                #~ self.response.write("ERROR: %s\n" % e)
                #~ sys.exit()
            #~ else:
                #~ if self.simulation:
                    #~ self.response.write("</code>\n")
                #~ else:
                    #~ self.response.write("OK\n")

            #~ if current_table in self.datetime_updates:
                #~ self.setup_table_datetime(current_table)

            reinit_tables.remove(current_table)
            self.response.write("\n")

        if reinit_tables != []:
            self.response.write("Error, Tables remaining:")
            self.response.write(table_names)
        self.response.write("</pre>")


    #_________________________________________________________________________
    # Zugriff auf ZIP-Datei

    def get_table_data(self, table_name):
        try:
            return self.ziparchiv.read(table_name+".sql")
        except Exception, e:
            self.response.write(
                "Can't get data for '%s': %s" % (table_name, e)
            )
            sys.exit()

    def get_table_names(self):
        """
        Die Tabellen namen sind die Dateinamen, außer info.txt
        """
        table_names = []
        dates = []
        for fileinfo in self.ziparchiv.infolist():
            date_time = fileinfo.date_time
            dates.append(date_time)

            if fileinfo.filename.endswith("/"):
                # Ist ein Verzeichniss
                continue
            filename = fileinfo.filename
            if filename == "info.txt":
                continue
            filename = os.path.splitext(filename)[0]
            table_names.append(filename)
        table_names.sort()

        max_date = max(dates) # Das neuste Dateidatum im ZIP-File

        # In Datetime-Object wandeln
        #~ self.newest_file_date = datetime.datetime(*max_date)

        max_date = str(max_date)
        max_date = time.strptime(
            max_date, "(%Y, %m, %d, %H, %M, %S)"
        )
        self.newest_file_date = self.tools.convert_time_to_sql(max_date)
        #~ self.newest_file_date = time.mktime(max_date)

        return table_names

    #_________________________________________________________________________
    # SQL

    def execute_many(self, command):
        """
        In der Install-Data-Datei sind in jeder Zeile ein SQL-Kommando,
        diese werden nach einander ausgeführt
        """
        counter = 0
        for line in command.split("\n"):
            if line=="": # Leere Zeilen überspringen
                continue
            self.execute(line)
            counter += 1
        return counter

    def execute(self, SQLcommand):

        SQLcommand = SQLcommand.replace("$$", self.db.tableprefix)

        if self.simulation:
            SQLcommand = str(SQLcommand) # Unicode wandeln

            SQLcommand = SQLcommand.encode("String_Escape")

            SQLcommand = cgi.escape(SQLcommand)
            self.response.write("%s\n" % SQLcommand)
            return

        if isinstance(SQLcommand, str):
            try:
                SQLcommand = unicode(SQLcommand, "utf8")
            except UnicodeDecodeError, e:
                self.response.write("Unicode Error: %s" % e)
                SQLcommand = unicode(SQLcommand, "utf8", errors="replace")

        print type(SQLcommand)

        if debug:
            self.db.cursor.execute(SQLcommand, do_prepare=False)
        else:
            try:
                self.db.cursor.execute(SQLcommand, do_prepare=False)
            except Exception, e:
                self.response.write(
                    "Error: '%s' in SQL-command:" % cgi.escape(str(e))
                )
                return False
        return True

    #_________________________________________________________________________

    def dump_data( self ):
        self.response.write("<h2>SQL Dump data:</h2>")
        print
        self.response.write("<pre>")
        for line in self.data.splitlines():
            self.response.write(cgi.escape(line))
        print "</pre>"







