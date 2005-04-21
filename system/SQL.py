#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__="0.0.1"


import sys

# MySQLdb - http://sourceforge.net/projects/mysql-python/
import MySQLdb as DBlib

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
        #~ try:
        self.connection = DBlib.connect(
            dbconf["dbHost"],
            dbconf["dbUserName"],
            dbconf["dbPassword"],
            dbconf["dbDatabaseName"]
        )
        self.cursor = self.connection.cursor()
        #~ except:
            #~ print "-"*50
            #~ print "Ein Fehler ist aufgetreten:"
            #~ print sys.exc_value
            #~ print "-"*50
            #~ return

    def execute( self, SQLcommand ):
        try:
            self.cursor.execute( SQLcommand )
        except:
            print "<h1>SQL-Fehler</h1>"
            print sys.exc_value
            sys.exit()

    def fetchall( self ):
        return self.cursor.fetchall()

    def close( self ):
        self.connection.close()

