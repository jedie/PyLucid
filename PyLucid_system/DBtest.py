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
import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import sys

import MySQLdb

# Interne PyLucid-Module einbinden
from system.config import dbconf



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





def testDB():
    print "<pre>"
    #~ print __file__
    print "Test DB-connect"
    print "dbHost:", dbconf["dbHost"]
    print "dbUserName:", dbconf["dbUserName"]
    print "dbDatabaseName:", dbconf["dbDatabaseName"]

    print "-"*80
    print "MySQLdb Info:"
    print "revision....:", MySQLdb.__revision__
    print "Version.....:", MySQLdb.__version__
    print "apilevel....:", MySQLdb.apilevel
    print "paramstyle..:", MySQLdb.paramstyle
    print "threadsaftey:", MySQLdb.threadsafety
    print "-"*80

    print "Connect...",
    try:
        connection = MySQLdb.connect(
            dbconf["dbHost"],
            dbconf["dbUserName"],
            dbconf["dbPassword"],
            dbconf["dbDatabaseName"]
        )
        cursor = connection.cursor()
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
    print "-"*80

    print "Test select:"

    SQLcommand = "SELECT name,title FROM lucid_pages"
    #~ SQLparameter = { "select":("name","title") }

    cursor.execute( SQLcommand)#, SQLparameter )
    for item in cursor.fetchall():
        print item
        testcodec( item, codecs )

    print "-"*80
    help(MySQLdb)
    print "<pre>"
    connection.close()
    sys.exit(0)


if __name__ == "__main__":
    testDB()