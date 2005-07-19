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
    * update und insert benutzen das SQLdb-Escaping. Die select-Funktion allerdings
      noch nicht!
    * Es wird immer das paramstyle 'format' benutzt. Also mit %s escaped
"""

__version__="0.0.7"

__history__="""
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



try:
    import MySQLdb
except ImportError, e:
    print "Content-type: text/html\n"
    print "<h1>Error</h1>"
    print "<h3>MySQLdb import error! Modul 'python-mysqldb' not installed???</h3>"
    print "<p>Error Msg.:<br/>%s</p>" % e
    print '<a href="http://sourceforge.net/projects/mysql-python/">MySQLdb project page</a>'
    import sys
    sys.exit(0)


#~ connr=0

class mySQL:
    """
    Klasse, die nur allgemeine SQL-Funktionen beinhaltet
    """
    def __init__( self, *args, **kwargs ):
        #~ print "Content-type: text/html\n"
        #~ global connr
        #~ connr+=1
        #~ print "<h1>Connect %s</h1>" % connr
        #~ if connr ==1: raise "Fehler!"

        self.conn           = MySQLdb.connect( *args, **kwargs )
        self.cursor         = self.conn.cursor( MySQLdb.cursors.DictCursor )
        self.tableprefix    = ""
        self.debug          = False

    def get( self, SQLcommand ):
        """kombiniert execute und fetchall mit Tabellennamenplatzhalter"""
        self.cursor.execute(
                SQLcommand.replace("$tableprefix$", self.tableprefix)
            )
        return self.cursor.fetchall()

    def fetchall( self, SQLcommand ):
        """ kombiniert execute und fetchall """
        self.cursor.execute( SQLcommand )
        return self.cursor.fetchall()

    def _make_values( self, values ):
        "Erstellt einen values-Tuple für cursor.execute()"
        if len( values ) == 1:
            return (values[0],)
        else:
            return tuple( values )

    def insert( self, table, data ):
        """
        Vereinfachter Insert, per dict
        data ist ein Dict, wobei die SQL-Felder den Key-Namen im Dict entsprechen muß!
        """
        items   = data.keys()
        values  = self._make_values( data.values() )

        SQLcommand = "INSERT INTO %(prefix)s%(table)s ( %(items)s ) VALUES ( %(values)s );" % {
                "prefix"        : self.tableprefix,
                "table"         : table,
                "items"         : ",".join( items ),
                "values"        : ",".join( ["%s"]*len(values) ) # Platzhalter für SQLdb-escape
            }

        if self.debug:
            print "-"*80
            print "db.insert - Debug:"
            print "SQLcommand.:",SQLcommand
            print "values.....:",values
            print "-"*80

        self.cursor.execute( SQLcommand, values )

    def update( self, table, data, where, limit=False ):
        """
        Vereinfachte SQL-update Funktion
        """
        items   = data.keys()
        values  = self._make_values( data.values() )

        if limit:
            limit = "LIMIT %s" % limit
        else:
            limit = ""

        SQLcommand = "UPDATE %(prefix)s%(table)s SET %(set)s WHERE %(where)s %(limit)s;" % {
                "prefix"    : self.tableprefix,
                "table"     : table,
                "set"       : ",".join( [str(i)+"=%s" for i in items] ),
                "where"     : "%s='%s'" % (where[0],where[1]),
                "limit"     : limit
            }

        if self.debug:
            print "-"*80
            print "db.update - Debug:"
            print "SQLcommand.:",SQLcommand
            print "values.....:",values
            print "-"*80

        self.cursor.execute( SQLcommand, values )

    def select( self, select_items, from_table, where=None, order=None, limit=None, maxrows=0, how=1 ):
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
        SQLcommand += " FROM `%s%s`" % ( self.tableprefix, from_table )

        if where != None:
            if type( where[0] ) == str:
                # es ist nur eine where-Regel vorhanden.
                # Damit die folgenden Anweisungen auch gehen
                where = [ where ]

            where_string = []
            for item in where:
                if type(item[1]) == int:
                    where_string.append( '`%s`=%s' % (item[0],item[1]) )
                else:
                    where_string.append( '`%s`="%s"' % (item[0],item[1]) )

            where_string = " and ".join( where_string )

            SQLcommand += ' WHERE %s' % where_string

        if order != None:
            SQLcommand += " ORDER BY `%s` %s" % order

        if limit != None:
            SQLcommand += " LIMIT %s,%s" % limit

        if self.debug:
            print "-"*80
            print "db.select - Debug:"
            print "SQLcommand:", SQLcommand

        return self.get( SQLcommand )
        RAWresult = self.get( SQLcommand )

        if self.debug:
            print "RAWresult:", RAWresult
            print "-"*80

        if select_items == "*":
            # Spezielle Auswertung bei "SELECT *"-Anfragen
            # Erstellt ein Dict mit den Namen der Tabellen-Felder
            select_items = self.cursor.description
            select_items = [i[0] for i in select_items]

        # Daten aufbereiten -> Packe alle Daten in ein Dict
        result = []
        itemlen = len(select_items)
        for line in RAWresult:
            temp = {}
            for i in xrange( itemlen ):
                if line[i] == None:
                    temp[ select_items[i] ] = ""
                else:
                    temp[ select_items[i] ] = line[i]
            result.append( temp )

        if result == []:
            return ()

        return result


    #~ def query_fetch_row( self, SQLcommand, values=() ):
        #~ """
        #~ Als ersartz für
            #~ connection.query( SQLcommand )
            #~ return connection.store_result().fetch_row( maxrows, how )
        #~ Diese Methoden gibt es leider erst in neueren Versionen von MySQLdb...
        #~ Bei meinem WebHoster läuft allerdings eine uralte Version :(

        #~ Meine nachgebaute Version liefert desc_dict und SQLresult zurück.
        #~ desc_dict ist ein Dict: [row-Name] = row-PositionsNr
        #~ SQLresult ist der ganz normale fetchall()-Tuple
        #~ """
        #~ self.cursor.execute( SQLcommand, values )
        #~ SQLresult   = self.cursor.fetchall()

        #~ index = 0
        #~ desc_dict = {}
        #~ for description in self.cursor.description:
            #~ desc_dict[ description[0] ] = index
            #~ index += 1

        #~ return desc_dict, SQLresult

    def exist_table_name( self, table_name ):
        """ Überprüft die existens eines Tabellen-Namens """
        self.cursor.execute( "SHOW TABLES" )
        for line in self.cursor.fetchall():
            if line[0] == table_name:
                return True
        return False

    def dump_select_result( self, result ):
        print "*** dumb select result ***"
        for i in xrange( len(result) ):
            print "%s - %s" % (i, result[i])

    def close( self ):
        "Connection schließen"
        self.conn.close()




if __name__ == "__main__":
    db = db(
            host    = "localhost",
            user    = "SQL-DB-Username",
            passwd  = "SQL-DB-Password",
            db      = "SQL-DB-Name"
        )

    # Prefix for all SQL-commands:
    db.tableprefix = "test_"

    # Prints all SQL-command:
    db.debug = True

    SQLcommand  = "CREATE TABLE %sTestTable (" % db.tableprefix
    SQLcommand += "id INT( 11 ) NOT NULL AUTO_INCREMENT,"
    SQLcommand += "data1 VARCHAR( 50 ) NOT NULL,"
    SQLcommand += "data2 VARCHAR( 50 ) NOT NULL,"
    SQLcommand += "PRIMARY KEY ( id )"
    SQLcommand += ") COMMENT = '%s - temporary test table';" % __file__

    print "\n\nCreat a temporary test table - execute SQL-command directly."
    try:
        db.cursor.execute( SQLcommand )
    except Exception, e:
        print "Can't create table: '%s'" % e


    print "\n\nSQL-insert Function:"
    db.insert(
            table = "TestTable",
            data  = { "data1" : "Value A 1", "data2" : "Value A 2" }
        )

    print "\n\nadds a new value:"
    db.insert(
            table = "TestTable",
            data  = { "data1" : "Value B 1", "data2" : "Value B 2" }
        )


    print "\n\nSQL-select Function (db.select):"
    result = db.select(
            select_items    = ["id","data1","data2"],
            from_table      = "TestTable",
            #~ where           = ("parent",0)#,debug=1
        )
    db.dump_select_result( result )


    print "\n\nUpdate an item (db.update)."
    data = { "data1" : "NewValue1!"}
    db.update(
            table   = "TestTable",
            data    = data,
            where   = ("id",1),
            limit   = 1
        )


    print "\n\nSee the new value (db.select):"
    result = db.select(
            select_items    = ["data1"],
            from_table      = "TestTable",
            where           = ("id",1)
        )
    db.dump_select_result( result )


    print "\n\nSee all values via SQL '*'-select:"
    result = db.select(
            select_items    = "*",
            from_table      = "TestTable",
            #~ where           = ("id",1)
        )
    db.dump_select_result( result )


    print "\n\nDelete the temporary test Table."
    db.cursor.execute( "DROP TABLE %sTestTable" % db.tableprefix )


    print "\n\nClose SQL-connection."
    db.close()







