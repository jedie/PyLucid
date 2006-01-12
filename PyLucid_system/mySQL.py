#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
MySQLdb wrapper

Allgemeine Routinen für eine einfachere SQL Benutzung

Benötigt MySQLdb download unter:
http://sourceforge.net/projects/mysql-python/


Information
-----------
Generell wird keine Tracebacks abgefangen, das muß immer im eigentlichen
Programm erledigt werden!

Wie man die Klasse benutzt, kann man unten sehen ;)



ToDo
----
    * Es wird immer das paramstyle 'format' benutzt. Also mit %s escaped
"""

__version__="0.4"

__history__="""
v0.4
    - Verwendet nun einen eigenen Dict-Cursor ( http://pythonwiki.pocoo.org/Dict_Cursor )
    - Nur mit MySQLdb getestet!
v0.3
    - Wenn fetchall verwendet wird, werden in self.last_SQLcommand und self.last_SQL_values die
        letzten SQL-Aktionen festgehalten. Dies kann gut, für Fehlerausgaben verwendet werden.
v0.2
    - insert() filtert nun automatisch Keys im Daten-Dict raus, die nicht als Spalte in der Tabelle vorkommen
    - NEU: get_table_field_information() und get_table_fields()
v0.1.1
    - NEU: decode_sql_results() - Alle Ergebnisse eines SQL-Aufrufs encoden
v0.1.0
    - Umbau, nun kann man den table_prefix bei einer Methode auch mit angeben, um auch an Tabellen zu
        kommen, die anders anfangen als in der config.py festgelegt.
v0.0.9
    - in update() wird nun auch die where-value SQL-Escaped
v0.0.8
    - bei select() werden nun auch die select-values mit der SQLdb escaped
    - methode _make_values() gelöscht und einfach durch tuple() erstetzt ;)
v0.0.7
    - Statt query_fetch_row() wird der Cursor jetzt mit MySQLdb.cursors.DictCursor erstellt.
        Somit liefern alle Abfragen ein dict zurück! Das ganze funktioniert auch mit der uralten
        MySQLdb v0.9.1
    - DEL: query_fetch_row()
    - NEU: fetchall()
v0.0.6
    - NEU: query_fetch_row() und exist_table_name()
v0.0.5
    - Stellt über self.conn das Connection-Objekt zur verfügung
v0.0.4
    - Bugfixes
    - Debugfunktion eingefügt
    - Beispiel hinzugefügt
    - SQL "*"-select verbessert.
v0.0.3
    - Allgemeine SQL insert und update Funktion eingefügt
    - SQL-where-Parameter kann nun auch meherere Bedingungen haben
v0.0.2
    - Allgemeine select-SQL-Anweisung
    - Fehlerausgabe bei fehlerhaften SQL-Anfrage
v0.0.1
    - erste Release
"""

from __future__ import generators

try:
    from utils import *
except ImportError:
    # Beim direkten Aufruf, zum Modul-Test!
    import sys
    sys.path.insert(0,"../PyLucid_python_backports")
    from utils import *

def error( msg, e):
    print "Content-type: text/html\n"
    print "<h1>Error</h1>"
    print "<h3>%s</h3>" % msg
    print "<p>Error Msg.:<br/>%s</p>" % e
    import sys
    sys.exit(0)



class mySQL:
    """
    Klasse, die nur allgemeine SQL-Funktionen beinhaltet
    """
    def __init__(self, PyLucid, debug=False):
        self.config = PyLucid["config"]

        # Zum speichern der letzten SQL-Statements (evtl. für Fehlerausgabe)
        self.last_SQLcommand = ""
        self.last_SQL_values = ()

        self.debug = debug
        self.tableprefix = self.config.dbconf["dbTablePrefix"]

        #~ try:
        self._make_connection()
        #~ except Exception, e:
            #~ error( "Can't connect to database!", e )

    def _make_connection(self):
        """
        Baut den connect mit dem Modul auf, welches in der config.py
        ausgewählt wurde.
        """
        if not self.config.dbconf.has_key("dbTyp"):
            self.config.dbconf["dbTyp"] = "MySQLdb"
            self.dbTyp = "MySQLdb"
        else:
            self.dbTyp = self.config.dbconf["dbTyp"]


        #_____________________________________________________________________________________________
        if self.dbTyp == "MySQLdb":
            try:
                import MySQLdb as dbapi
            except ImportError, e:
                msg  = "MySQLdb import error! Modul"
                msg += """ '<a href="http://sourceforge.net/projects/mysql-python/">python-mysqldb</a>' """
                msg += "not installed???"""
                error( msg, e )

            self.conn = WrappedConnection(
                dbapi.connect(
                    host    = self.config.dbconf["dbHost"],
                    user    = self.config.dbconf["dbUserName"],
                    passwd  = self.config.dbconf["dbPassword"],
                    db      = self.config.dbconf["dbDatabaseName"],
                ),
                placeholder = '%s',
                prefix = self.tableprefix
            )
            self.cursor = self.conn.cursor()

        #_____________________________________________________________________________________________
        elif self.dbTyp == "sqlite":
            try:
                from pysqlite2 import dbapi2 as dbapi
            except ImportError, e:
                msg  = "pysqlite import error! Modul"
                msg += """ '<a href="http://pysqlite.org">pysqlite-mysqldb</a>' """
                msg += "not installed???"""
                error( msg, e )

            self.conn   = dbapi.connect( "%s.db" % self.config.dbconf["dbDatabaseName"] )
            self.cursor = self.conn.cursor(factory=DictCursor)
        #_____________________________________________________________________________________________
        elif self.dbTyp == "odbc":
            try:
                import odbc
            except ImportError, e:
                msg  = "odbc import error! Mark Hammond's"
                msg += """ '<a href="http://starship.python.net/crew/mhammond/win32/">Win32all</a>' """
                msg += "not installed???"""
                error( msg, e )

            self.conn   = odbc.odbc()
                #~ host    = self.config.dbconf["dbHost"],
                #~ user    = self.config.dbconf["dbUserName"],
                #~ passwd  = self.config.dbconf["dbPassword"],
                #~ db      = self.config.dbconf["dbDatabaseName"],
            #~ )
            self.cursor = self.conn.cursor( odbc.cursors.DictCursor )
        #_____________________________________________________________________________________________
        elif self.dbTyp == "adodb":
            self.escapechar = "?"
            try:
                import adodbapi as dbapi
            except ImportError, e:
                msg  = "adodbapi import error!"
                msg += """ '<a href="http://adodbapi.sourceforge.net/">adodbapi</a>' """
                msg += "not installed???"""
                error( msg, e )

            DSN_info = (
                "DRIVER=SQL Server;"
                "SERVER=%s;"
                "DATABASE=%s;"
                "UID=%s;"
                "PASSWORD=%s;"
            ) % (
                dbconf["dbHost"],
                dbconf["dbDatabaseName"],
                dbconf["dbUserName"],
                dbconf["dbPassword"],
            )
            self.conn   = dbapi.connect(DSN_info)
            self.cursor = self.conn.cursor()
        else:
            raise ImportError("Unknow DB-Modul '%s' (look at config.py!):" % db_module)

    #~ def get(self, SQLcommand, SQL_values = (), table_prefix=None):
        #~ """kombiniert execute und fetchall mit Tabellennamenplatzhalter"""
        #~ if table_prefix == None: table_prefix = self.tableprefix
        #~ self.cursor.execute(
                #~ SQLcommand.replace("$tableprefix$", self.tableprefix),
                #~ tuple(SQL_values)
            #~ )
        #~ return self.cursor.fetchall()

    def fetchall(self, SQLcommand, SQL_values = ()):
        """ kombiniert execute und fetchall """
        self.last_SQLcommand = SQLcommand
        self.last_SQL_values = SQL_values
        try:
            self.cursor.execute(SQLcommand, SQL_values)
        except Exception, e:
            raise Exception("execute Error: %s --- SQL-command: %s --- SQL-values: %s" % (
                e, SQLcommand, SQL_values
                )
            )
        try:
            result = self.cursor.fetchall()
        except Exception, e:
            raise Exception("fetchall Error: %s --- SQL-command: %s --- SQL-values: %s" % (
                e, SQLcommand, SQL_values
                )
            )

        return result

    def get_tables(self):
        """
        Liefert alle Tabellennamen die das self.tableprefix haben
        """
        tables = []
        for table in self.fetchall("SHOW TABLES"):
            tablename = table.values()[0]
            if tablename.startswith( table_prefix):
                tables.append( tablename )
        return tables

    def insert(self, table, data, debug=False):
        """
        Vereinfachter Insert, per dict
        data ist ein Dict, wobei die SQL-Felder den Key-Namen im Dict entsprechen muß, dabei werden Keys, die nicht
        in der Tabelle als Spalte vorkommt vorher rausgefiltert
        """
        # Nicht vorhandene Tabellen-Spalten aus dem Daten-Dict löschen
        field_list = self.get_table_fields(table)
        if debug or self.debug:
            print "field_list:", field_list
        index = 0
        for key in list(data.keys()):
            if not key in field_list:
                del data[key]
            index += 1

        items  = data.keys()
        values = tuple(data.values())

        SQLcommand = "INSERT INTO $$%(table)s ( %(items)s ) VALUES ( %(values)s );" % {
                "table"         : table,
                "items"         : ",".join( items ),
                "values"        : ",".join( ["%s"]*len(values) ) # Platzhalter für SQLdb-escape
            }

        if debug or self.debug:
            print "-"*80
            print "db.insert - Debug:"
            print "SQLcommand.:", SQLcommand
            print "values.....:", values
            print "-"*80

        return self.fetchall(SQLcommand, values)

    def update(self, table, data, where, limit=False):
        """
        Vereinfachte SQL-update Funktion
        """
        data_keys   = data.keys()

        values      = data.values()
        values.append(where[1])
        values      = tuple(values)

        if limit:
            limit = "LIMIT %s" % limit
        else:
            limit = ""

        SQLcommand = "UPDATE $$%(table)s SET %(set)s WHERE %(where)s %(limit)s;" % {
                "table"     : table,
                "set"       : ",".join( [str(i)+"=%s" for i in data_keys] ),
                "where"     : where[0] + "=%s",
                "limit"     : limit
            }

        if self.debug:
            print "-"*80
            print "db.update - Debug:"
            print "SQLcommand.:", SQLcommand
            print "values.....:", values
            print "-"*80

        return self.fetchall(SQLcommand, values)

    def select(self, select_items, from_table, where=None, order=None, limit=None,
            maxrows=0, how=1, debug=False):
        """
        Allgemeine SQL-SELECT Anweisung
        where, order und limit sind optional

        where
        -----
        Die where Klausel ist ein wenig special.

        einfache where Klausel:
        where=("parent",0) ===> WHERE `parent`="0"

        mehrfache where Klausel:
        where=[("parent",0),("id",0)] ===> WHERE `parent`="0" and `id`="0"

        maxrows - Anzahl der zurückgegebenen Datensätze, =0 alle Datensätze
        how     - Form der zurückgegebenen Daten. =1 -> als Dict, =0 als Tuple
        """
        SQLcommand = "SELECT " + ",".join( select_items )
        SQLcommand += " FROM $$%s" % from_table

        SQL_parameters_values = []

        if where != None:
            where_string, SQL_parameters_values = self._make_where( where )
            SQLcommand += where_string

        if order != None:
            try:
                SQLcommand += " ORDER BY %s %s" % order
            except TypeError,e:
                raise TypeError("Error in db.select() ORDER statement (must be a tuple or List): %s" % e)
        if limit != None:
            try:
                SQLcommand += " LIMIT %s,%s" % limit
            except TypeError,e:
                raise TypeError("Error in db.select() LIMIT statement (must be a tuple or List): %s" % e)

        if self.debug or debug:
            print "-"*80
            print "db.select - Debug:"
            print "SQLcommand.:", SQLcommand
            print "values.....:", SQL_parameters_values

        return self.fetchall(SQLcommand, SQL_parameters_values)

    def delete(self, table, where, limit=1, debug=False):
        """
        DELETE FROM table WHERE id=1 LIMIT 1
        """
        SQLcommand = "DELETE FROM $$%s" % table

        where_string, SQL_parameters_values = self._make_where(where)

        SQLcommand += where_string
        SQLcommand += " LIMIT %s" % limit

        if self.debug or debug:
            print "-"*80
            print "db.delete - Debug:"
            print "SQLcommand:", SQLcommand
            print "values.....:", SQL_parameters_values
            print "-"*80

        return self.fetchall(SQLcommand, SQL_parameters_values)

    #_____________________________________________________________________________________________

    def _make_where(self, where):
        """
        Baut ein where-Statemant und die passenden SQL-Values zusammen
        """
        if type( where[0] ) == str:
            # es ist nur eine where-Regel vorhanden.
            # Damit die folgenden Anweisungen auch gehen
            where = [ where ]

        where_string            = []
        SQL_parameters_values   = []

        for item in where:
            where_string.append( item[0] + "=%s" )
            SQL_parameters_values.append( item[1] )

        where_string = ' WHERE %s' % " and ".join( where_string )

        return where_string, tuple(SQL_parameters_values)

    #_____________________________________________________________________________________________

    def get_table_field_information(self, table_name, debug=False):
        """
        Liefert "SHOW FIELDS"-Information in Roh-Daten zurück
        """
        if self.dbTyp == "adodb":
            SQLcommand = (
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_NAME = '$$%s';"
            ) % table_name
        else:
            SQLcommand = "SHOW FIELDS FROM $$%s;" % table_name

        if self.debug or debug:
            print "-"*80
            print "get_table_field_information:", SQLcommand

        result = self.fetchall(SQLcommand)
        if self.debug or debug:
            print "result:", result
        return result

    def get_table_fields(self, table_name):
        """
        Liefert nur die Tabellen-Feld-Namen zurück
        """
        field_information = self.get_table_field_information(table_name)

        if self.dbTyp == "adodb":
            return field_information

        result = []
        for column in field_information:
            result.append(column["Field"])
        return result

    def exist_table_name(self, table_name):
        """ Überprüft die existens eines Tabellen-Namens """
        self.cursor.execute( "SHOW TABLES" )
        for line in self.cursor.fetchall():
            if line[0] == table_name:
                return True
        return False

    def decode_sql_results(self, sql_results, codec="UTF-8"):
        """
        Alle Ergebnisse eines SQL-Aufrufs encoden
        """
        post_error = False
        for line in sql_results:
            for k,v in line.iteritems():
                if type(v)!=str:
                    continue
                try:
                    line[k] = v.decode(codec)
                except Exception, e:
                    if not post_error:
                        # Fehler nur einmal anzeigen
                        self.page_msg("decode_sql_results() error: %s" % e)
                        post_error = True
                        self.page_msg("line:", line)
        return sql_results

    #_____________________________________________________________________________________________

    def dump_select_result(self, result):
        print "*** dumb select result ***"
        for i in xrange( len(result)):
            print "%s - %s" % (i, result[i])

    def close(self):
        "Connection schließen"
        self.conn.close()




class WrappedConnection(object):

    def __init__(self, cnx, placeholder, prefix=''):
        self.cnx = cnx
        self.placeholder = placeholder
        self.prefix = prefix

    def cursor(self):
        return IterableDictCursor(self.cnx, self.placeholder, self.prefix)

    def __getattr__(self, attr):
        #~ try:
        return getattr(self.cnx, attr)
        #~ except AttributeError, e:
            #~ raise
        #~ except Exception, e:
            #~ print "XXXX:", e.__class__
            #~ print e
            #~ print "---"
            #~ raise



class IterableDictCursor(object):

    def __init__(self, cnx, placeholder, prefix):
        self._cursor = cnx.cursor()
        self._placeholder = placeholder
        self._prefix = prefix

    def __getattr__(self, attr):
        if attr == 'lastrowid':
            if hasattr(self._cursor, 'insert_id'):
                # Patch für alte MySQLdb Version, die kein lastrowid (s. PEP-0249)
                # besitzt, aber eine insert_id() Methode hat
                return self._cursor.insert_id()
        return getattr(self._cursor, attr)

    def prepare_sql(self, sql):
        return sql.replace('$$', self._prefix)\
                  .replace('?', self._placeholder)

    def execute(self, sql, values=None):
        args = [self.prepare_sql(sql)]
        if values:
            args.append(values)
        self._cursor.execute(*tuple(args))

    def fetchone(self):
        row = self._cursor.fetchone()
        if not row:
            return ()
        result = {}
        for idx, col in enumerate(self._cursor.description):
            result[col[0]] = row[idx]
        return result

    def fetchall(self):
        rows = self._cursor.fetchall()
        result = []
        for row in rows:
            tmp = {}
            for idx, col in enumerate(self._cursor.description):
                tmp[col[0]] = row[idx]
            result.append(tmp)
        return result

    def __iter__(self):
        while True:
            row = self.fetchone()
            if not row:
                return
            yield row














if __name__ == "__main__":
    import cgitb;cgitb.enable()
    print "Content-type: text/html; charset=utf-8\r\n"
    print "<pre>"

    import sys
    sys.path.insert(0,"../")
    import config # PyLucid's "config.py"

    PyLucid = {
        "config": config
    }
    db = mySQL(PyLucid)

    #~ del(db.cursor.lastrowid)

    print "SHOW TABLE STATUS:", db.cursor.execute("SHOW TABLE STATUS")
    print "SHOW TABLES:", db.cursor.execute("SHOW TABLES")

    # Prints all SQL-command:
    db.debug = True

    SQLcommand  = "CREATE TABLE $$TestTable ("
    SQLcommand += "id INT( 11 ) NOT NULL AUTO_INCREMENT,"
    SQLcommand += "data1 VARCHAR( 50 ) NOT NULL,"
    SQLcommand += "data2 VARCHAR( 50 ) NOT NULL,"
    SQLcommand += "PRIMARY KEY ( id )"
    SQLcommand += ") COMMENT = 'Temporary test table';"

    print "\n\nCreat a temporary test table - execute SQL-command directly."
    try:
        db.cursor.execute( SQLcommand )
    except Exception, e:
        print "Can't create table:", e
        #~ raise


    print "\n\nSQL-insert Function:"
    db.insert(
            table = "TestTable",
            data  = { "data1" : "Value A 1", "data2" : "Value A 2" }
        )
    print "cursor.lastrowid:", db.cursor.lastrowid

    print "\n\nadds a new value:"
    db.insert(
            table = "TestTable",
            data  = { "data1" : "Value B 1", "data2" : "Value B 2" }
        )
    print "cursor.lastrowid:", db.cursor.lastrowid

    print "\n\nSQL-select Function (db.select):"
    result = db.select(
            select_items    = ["id","data1","data2"],
            from_table      = "TestTable",
            #~ where           = ("parent",0)#,debug=1
        )
    db.dump_select_result( result )

    print "\n\ndelete a value:"
    db.delete(
            table = "TestTable",
            where = ("id",1)
        )
    print "cursor.lastrowid:", db.cursor.lastrowid

    print "\n\nUpdate an item (db.update)."
    data = { "data1" : "NewValue1!"}
    db.update(
            table   = "TestTable",
            data    = data,
            where   = ("id",1),
            limit   = 1
        )
    print "cursor.lastrowid:", db.cursor.lastrowid

    print "\n\nSee the new value (db.select):"
    result = db.select(
            select_items    = ["data1"],
            from_table      = "TestTable",
            where           = ("id",1)
        )
    db.dump_select_result( result )


    print "\n\nSee all values via SQL '*'-select and ordet it by 'id':"
    result = db.select(
            select_items    = "*",
            from_table      = "TestTable",
            order           = ("id","ASC"),
        )
    db.dump_select_result( result )

    print "\nCheck SQL:",
    if result != [{'data1': 'Value B 1', 'id': 2L, 'data2': 'Value B 2'}]:
        print "ERROR: Result not right!"
    else:
        print "OK, Data are as assumed."


    print "\n\nDelete the temporary test Table."
    db.cursor.execute( "DROP TABLE %sTestTable" % db.tableprefix )


    print "\n\nClose SQL-connection."
    db.close()

    print "<pre>"







