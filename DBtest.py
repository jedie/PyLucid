#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Testet den Zugriff auf die Datenbank, bzw. die richtigkeit
der Daten in ./system/config.dbconf
"""

__version__="0.0.1"

__history__="""
v0.0.1
    - erste Release
"""

print "Content-type: text/html\n"
#~ import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import sys

import MySQLdb

# Interne PyLucid-Module einbinden
from config import dbconf



def testcodec( string_list, codec_list ):
    for item in string_list:
        for codec in codec_list:
            try:
                print item.encode( codec ),
                print " - encode:", codec
            except:
                pass
            try:
                print item.decode( codec ),
                print " - decode:", codec
            except:
                pass

codecs = (
    "ascii","latin_1",
    "utf_16","utf_16_be","utf_16_le","utf_7","utf_8",
    "raw_unicode_escape","string_escape",
    "unicode_escape","unicode_internal"
)



class test_db:
    def __init__( self ):
        print "<pre>"
        self.print_info()
        self.connect()
        self.select_datetime()
        #~ self.select_test()
        #~ self.codec_test()
        #~ help(MySQLdb)
        print "</pre>"
        self.connection.close()

    def _print_info( self, txt ):
        print
        print "_"*80
        print txt
        print "-"*80

    def print_info( self ):
        self._print_info( "Information" )

        print "dbHost:", dbconf["dbHost"]
        print "dbUserName:", dbconf["dbUserName"]
        print "dbDatabaseName:", dbconf["dbDatabaseName"]

        print "\nMySQLdb Info:"
        print "revision....:", MySQLdb.__revision__
        print "Version.....:", MySQLdb.__version__
        print "apilevel....:", MySQLdb.apilevel
        print "paramstyle..:", MySQLdb.paramstyle
        print "threadsaftey:", MySQLdb.threadsafety
        #~ print MySQLdb.cursors.DictCursor

    def connect( self ):
        self._print_info( "Connect to SQL" )
        try:
            self.connection = MySQLdb.connect(
                dbconf["dbHost"],
                dbconf["dbUserName"],
                dbconf["dbPassword"],
                dbconf["dbDatabaseName"]
            )
            self.cursor = self.connection.cursor( MySQLdb.cursors.DictCursor )
        except Exception, e:
            print 'Error:'
            print
            print e
            print
            import traceback
            import StringIO
            tb = StringIO.StringIO()
            traceback.print_exc(file=tb)
            print tb.getvalue()
            print "</pre>"
            sys.exit(1)

        print "OK!"

    def select_datetime( self ):
        SQLcommand = "SELECT lastupdatetime FROM lucid_pages"# LIMIT 0,50"
        self.cursor.execute( SQLcommand)#, SQLparameter )
        for item in self.cursor.fetchall():
            print item, type(item["lastupdatetime"])

    def select_test( self ):
        SQLcommand = "SELECT name,title FROM lucid_pages LIMIT 0,10"
        self.cursor.execute( SQLcommand)#, SQLparameter )
        for item in self.cursor.fetchall():
            print item

    def codec_test( self ):
        self._print_info( "codec test" )

        SQLcommand = "SELECT name,title FROM lucid_pages LIMIT 0,3"
        #~ SQLparameter = { "select":("name","title") }

        self.cursor.execute( SQLcommand)#, SQLparameter )
        for item in self.cursor.fetchall():
            print item
            testcodec( item, codecs )

if __name__ == "__main__":
    test_db()