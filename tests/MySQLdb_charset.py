#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Debugging für CGI-Skripte 'einschalten'
#~ import cgitb; cgitb.enable()
print "Content-Type: text/plain;charset=utf-8\n"
print "-==[MySQLdb charset test]==-\n"


import MySQLdb

print "MySQLdb Version:", MySQLdb.__version__
print "MySQLdb version_info:", MySQLdb.version_info


OUT_ENCODING = "utf-8"



#~ TEST_ENCODINGS = ("unicode", "utf-8", "latin-1", "iso-8859-15", "utf_16_be")
#~ TEST_STRING = u"Test äöüß"

# latin-1 test:
TEST_ENCODINGS = ("unicode", "utf-8", "latin-1", "utf_16_be")
TEST_STRING = u"".join([unichr(i) for i in xrange(0, 256)])



import sys
sys.path.insert(0,"..")
from config import config # PyLucid config file

connection = MySQLdb.Connect(
    host    = config["dbHost"],
    user    = config["dbUserName"],
    passwd  = config["dbPassword"],
    db      = config["dbDatabaseName"],
)
cursor=connection.cursor()


# Funktioniert erst mit MySQL =>v4.1
#~ cursor.execute('set character set %s;', ("utf8",))
#~ server_encoding = "utf-8"


print "\nMySQL server encoding:"
cursor.execute("SHOW VARIABLES LIKE %s;", ("character_set_server",))
server_encoding = cursor.fetchone()[1]
print "\tMySQL variable 'character_set_server':", server_encoding
print "\tconnection.character_set_name:", connection.character_set_name()



print
print "-"*79


def test(encoding):
    if encoding == "unicode":
        print "inser the teststring in unicode!"
        db_input = TEST_STRING
    else:
        print "insert the teststring encoded in '%s':" % encoding
        db_input = TEST_STRING.encode(encoding)

    print "INSERT & SELECT...",
    cursor.execute("INSERT INTO temp_test (txt) VALUES (%s);", (db_input,))
    connection.commit()
    cursor.execute("SELECT * FROM temp_test;")
    db_output = cursor.fetchone()[0]
    print "OK"

    print "db_input...: %s..." % repr(db_input)[:70]
    print "db_output..: %s..." % repr(db_output)[:70]

    print "Encode db output with server encoding '%s'..." % server_encoding,
    try:
        db_output = db_output.decode(server_encoding)
    except Exception, e:
        print "ERROR:", e
    else:
        print "OK"

        print "Is test-String == db output:", db_output == TEST_STRING




try:
    try:
        print "CREATE TABLE temp_test...",
        cursor.execute("CREATE TABLE temp_test (txt varchar(65535));")
        print "OK"
    except Exception, e:
        print "Fehler:", e



    for encoding in TEST_ENCODINGS:
        print
        print "-"*79
        test(encoding)



    try:
        print "\nDROP TABLE...",
        cursor.execute("DROP TABLE temp_test;")
        print "OK"
    except Exception, e:
        print "Fehler:", e
finally:
    print "\nClose Connection...",
    connection.close()
    print "OK"

