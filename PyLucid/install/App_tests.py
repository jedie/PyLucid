#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

import os, sys

from PyLucid.install.ObjectApp_Base import ObjectApp_Base


class tests(ObjectApp_Base):
    "4. info / tests"
    def db_info(self, currentAction = None):
        "DB connection Information"
        self._write_info()

        subactions = [
            "_connect_information", "_show_grants",
            "_show_variables",
            "_show_engines", "_show_characterset"
        ]
        # Menü anzeigen und evtl. ausgewählte Methode aufrufen
        self._autoSubAction(subactions, currentAction)

    def _connect_information(self):
        #___________________________________
        # db preferences

        self.response.write('<fieldset><legend>db preferences</legend><pre>')
        for k,v in self.request.preferences.iteritems():
            if not k.startswith("db"):
                continue
            if k == "dbPassword":
                v = "***"
            self.response.write("%-25s: %s\n" % (k,v))
        self.response.write("</pre></fieldset>")

        #___________________________________
        # db info

        self.response.write('<fieldset><legend>db info</legend><pre>')

        self.response.write("%-25s: " % "dbapi module version")
        try:
            self.response.write(
                "%s %s\n" % (
                    self._db.dbapi.__name__, self._db.dbapi.__version__
                )
            )
        except Exception, e:
            self.response.write("(Error: %s)" % e)

        self.response.write(
            "%-25s: %s (raw version String: '%s')\n" % (
                "SQL-Server version",
                self._db.server_version, self._db.RAWserver_version
            )
        )
        self.response.write(
            "%-25s: %s\n" % ("paramstyle", self._db.paramstyle)
        )
        self.response.write(
            "%-25s: %s\n" % ("placeholder", self._db.placeholder)
        )
        self.response.write(
            "%-25s: %s\n" % ("used db encoding", self._db.encoding)
        )

        self.response.write("</pre></fieldset>")

        #___________________________________
        # info
        self.response.write('<fieldset><legend>info</legend><pre>')

        sys_version = sys.version.replace("\n", " ")
        self.response.write("%-25s: %s\n" % ("Python version",sys_version))

        if hasattr(os,"uname"): # Nicht unter Windows verfügbar
            self.response.write(
                "%-25s: %s\n" % ("os.uname()", " - ".join(os.uname()))
            )

        self.response.write("</pre></fieldset>")

    def _show_variables(self):
        """
        http://dev.mysql.com/doc/refman/4.1/en/show-variables.html
        """
        self._execute_verbose(
            "List of all SQL server variables",
            "SHOW VARIABLES;", primaryKey="Variable_name"
        )

    def _show_grants(self):
        """
        http://dev.mysql.com/doc/refman/4.1/en/show-grants.html

        Rechte Anzeigen
        Für MySQL 4.1 reicht "SHOW GRANTS;"
        Für MySQL =>4.1 müßte eigentlich "SHOW GRANTS FOR CURRENT_USER;"
        funktionieren. Geht aber bei meinen tests nicht wirklich.
        Wenn allerdings der Username explizit angegeben wird, klappt es, nur
        nicht, wenn über eine Remote-Verbindung mit dem SQL-Server kommuniziert
        wird?!?!?
        Also probieren wir einfach rum:
        """
        def print_result():
            result = self._db.cursor.fetchall()
            # Daten als HTML-Tabelle ins response Obj. schreiben lassen:
            self._tools.writeDictListTable(result, self.response)

        self.response.write("<h3>Database user rights:</h3>\n")
        try:
            self._db.cursor.execute("SHOW GRANTS;")
        except Exception, e:
            pass
        else:
            print_result()
            return

        try:
            self._db.cursor.execute("SHOW GRANTS FOR CURRENT_USER;")
        except Exception, e:
            pass
        else:
            print_result()
            return

        SQLcommand = "SHOW GRANTS FOR %s;" % \
                                        self.request.preferences["dbUserName"]
        try:
            self._db.cursor.execute(SQLcommand)
        except Exception, e:
            self.response.write("<pre>\n")
            self.response.write("execude ERROR: %s\n" % e)
            self.response.write("SQLcommand: %s\n" % SQLcommand)
            self.response.write("</pre>\n")
            return
        else:
            print_result()

    def _show_engines(self):
        """
        http://dev.mysql.com/doc/refman/4.1/en/show-engines.html
        """
        if self._db.server_version < (4,1,2):
            msg = (
                "<p><strong>Note:</strong>"
                " MySQL 4.1.2 required for 'SHOW ENGINE;'\n"
                " (<small>Your SQL Version: %s)</small>"
            ) % self._db.RAWserver_version
            self.response.write(msg)

        self._execute_verbose(
            "Available db storage engines",
            "SHOW ENGINES", primaryKey="Engine"
        )

        self._execute_verbose(
            "Available db storage engines",
            "SHOW TABLE TYPES", primaryKey="Engine"
        )

    def _show_characterset(self):
        """
        http://dev.mysql.com/doc/refman/4.1/en/show-character-set.html
        """
        if self._db.server_version < (4,1,0):
            msg = (
                "<p><strong>Note:</strong>"
                " MySQL 4.1.0 required for 'SHOW CHARACTER SET;'\n"
                " (<small>Your SQL Version: %s)</small>"
            ) % self._db.RAWserver_version
            self.response.write(msg)

        self._execute_verbose(
            "Available character set",
            "SHOW CHARACTER SET", primaryKey="Charset"
        )

    #_________________________________________________________________________

    def table_info(self, table_name=None):
        "DB Table info"
        self._write_info()

        self.response.write("<h3>table list</h3>")
        self.response.write(
            "<small>(only tables with prefix '%s')</small>" % \
                                                    self._db.tableprefix
        )
        self.response.write("<ul>")
        tableNameList = self._db.get_tables()
        for tableName in tableNameList:
            url = self._URLs.installSubAction(tableName)
            line = (
                '<li><a href="%(url)s">%(name)s</a></li>'
            ) % {
                "url": url,
                "name": tableName
            }
            self.response.write(line)

        self.response.write("</ul>")


        if table_name == None:
            # Noch keine Tabelle ausgewählt
            return
        elif table_name not in tableNameList:
            self.response.write("Error! '%s' not exists!" % table_name)
            return

        #~ self._execute_verbose("SHOW FULL TABLES;")
        #~ self._execute_verbose("SHOW TABLE STATUS FROM %s;" % table_name)
        self._execute_verbose("CHECK TABLE %s;" % table_name)
        self._execute_verbose("ANALYZE TABLE %s;" % table_name)
        self._execute_verbose(
            "SHOW FULL COLUMNS FROM %s;" % table_name,
            primaryKey="Field"
        )
        self._execute_verbose("SHOW INDEX FROM %s;" % table_name)

        SQLcommand = "SHOW CREATE TABLE %s" % table_name
        self._execute_verbose(SQLcommand, primaryKey="Table")


    def module_admin_info(self, module_id=None):
        "Information about installed modules"
        self._write_info()

        #~ self._URLs["current_action"] = self._URLs["base"]
        module_admin = self._get_module_admin()

        module_admin.debug_installed_modules_info(module_id)


    def path_check(self):
        "Path and URL check"
        self._write_info()

        self.response.write("<h4>generates automatically:</h4>")
        self.response.write("<pre>")
        for k,v in self._URLs.iteritems():
            self.response.write("%15s: %s\n" % (k,v))
        self.response.write("</pre>")
        self.response.write("<hr/>")


    def _execute_verbose(self, title, SQLcommand=None, primaryKey=""):
        if SQLcommand == None:
            SQLcommand = title

        self.response.write("<h3>%s:</h3>\n" % title.rstrip(";"))

        try:
            self._db.cursor.execute(SQLcommand)
        except Exception, e:
            self.response.write("<pre>\n")
            self.response.write("execude ERROR: %s\n" % e)
            self.response.write("SQLcommand: %s\n" % SQLcommand)
            self.response.write("</pre>\n")
            return

        result = self._db.cursor.fetchall()

        # Daten als HTML-Tabelle ins response Obj. schreiben lassen:
        self._tools.writeDictListTable(result, self.response, primaryKey)










