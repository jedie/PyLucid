#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Anbindung an die SQL-Datenbank mittels MySQLdb

Benötigt MySQLdb download unter:
http://sourceforge.net/projects/mysql-python/
"""

__version__="0.0.3"

__history__="""
v0.0.3
    - SQL-where-Parameter kann nun auch meherere Bedingungen haben
v0.0.2
    - Allgemeine select-SQL-Anweisung
    - Fehlerausgabe bei fehlerhaften SQL-Anfrage
v0.0.1
    - erste Release
"""

# Python-Basis Module einbinden
import sys


import MySQLdb as DBlib

# Interne PyLucid-Module einbinden
from config import dbconf

#~ $dbLibrary='dbMySQL';
#~ $dbHost='localhost';
#~ $dbDatabaseName='derDatenbankname';
#~ $dbUserName='derUsername';
#~ $dbPassword='einPasswort';
#~ $dbTablePrefix='prefix_';




class db:
    def __init__( self ):
        self.connect()

    def connect( self ):
        try:
            self.connection = DBlib.connect(
                dbconf["dbHost"],
                dbconf["dbUserName"],
                dbconf["dbPassword"],
                dbconf["dbDatabaseName"]
            )
            self.cursor = self.connection.cursor()
        except Exception, e:
            print 'Content-Type: text/plain\r\n\r\n',
            print __file__
            print 'internal error:'
            print
            print e
            print
            import traceback
            import StringIO
            tb = StringIO.StringIO()
            traceback.print_exc(file=tb)
            print tb.getvalue()
            sys.exit(1)

    def execute( self, SQLcommand ):
        try:
            self.cursor.execute( SQLcommand )
        except:
            print "<h1>SQL-Fehler</h1>"
            print "<pre>SQLcommand:\n%s\n</pre>" % SQLcommand
            print sys.exc_value
            sys.exit()

    def fetchall( self ):
        return self.cursor.fetchall()

    def get( self, SQLcommand ):
        "kombiniert execute und fetchall"
        self.execute( SQLcommand )
        return self.cursor.fetchall()

    def select( self, select_items, from_table, where=None, order=None, limit=None, debug=False ):
        """
        Allgemeine SQL-SELECT Anweisung
        where, oeder und limit sind optional
        mit sebug=True wird das SQL-Kommando generiert, ausgegeben und sys.exit()

        where
        -----
        Die where Klausel ist ein wenig special.

        einfache where Klausel:
        where=("parent",0) ===> WHERE `parent`="0"

        mehrfache where Klausel:
        where=[("parent",0),("id",0)] ===> WHERE `parent`="0" and `id`="0"
        """

        select_String = ["`%s`" % i for i in select_items]

        SQLcommand = "SELECT " + ",".join( select_String )
        SQLcommand += " FROM `%s%s`" % ( dbconf["dbTablePrefix"], from_table )

        if where != None:
            if type( where[0] ) == type(""):
                # Damit die folgenden Anweisungen auch gehen
                where = [ where ]

            where_string = ['`%s`="%s"' % (i[0],i[1]) for i in where]
            where_string = " and ".join( where_string )

            SQLcommand += ' WHERE %s' % where_string

        if order != None:
            SQLcommand += " ORDER BY `%s` %s" % order

        if limit != None:
            SQLcommand += " LIMIT %s,%s" % limit

        if debug == True:
            print ">>> (debug) SQL-command:"
            print "-"*80
            print SQLcommand
            print "-"*80
            sys.exit()

        RAWresult = self.get( SQLcommand )

        result = []
        itemlen = len(select_items)
        for line in RAWresult:
            temp = {}
            for i in xrange( itemlen ):
                temp[ select_items[i] ] = line[i]
            result.append( temp )

        return result

    def dump_select_result( self, result ):
        for line in result:
            print line

    def close( self ):
        self.connection.close()

if __name__ == "__main__":
    print ">Loaker Test:"
    db = db()

    result = db.select(
        select_items    = ["id","name"],
        from_table      = "pages",
        where           = ("parent",0)
    )
    db.dump_select_result( result )

    result = db.select(
        select_items    = ["id","name"],
        from_table      = "pages",
        where           = [("parent",0),("id",0)]
    )
    db.dump_select_result( result )

