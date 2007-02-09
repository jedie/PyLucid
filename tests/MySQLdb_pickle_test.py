#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
MySQLdb encodning test, testing with pickled Data.

auch als CGI ausführbar!
"""

print "Content-type: text/plain; charset=utf-8\r\n\r\n"
print "--==[ MySQLdb pickle Test ]==--"


import sys
sys.stderr = sys.stdout # Tracebacks anzeigen (CGI)

import warnings, MySQLdb

try:
    import cPickle as pickle
except ImportError:
    import pickle



#~ USED_PICKLE_PROTOCOL = 0
USED_PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL
USED_ENCODING = "utf8"
#~ USED_ENCODING = "latin1"
#~ USED_ENCODING = "ascii"




# MySQL Warnungen anzeigen:
# siehe: http://dev.mysql.com/doc/refman/5.1/en/show-warnings.html
warnings.filterwarnings("always",category=Warning)


print "MySQLdb Version:", MySQLdb.__version__
print "MySQLdb version_info:", MySQLdb.version_info
print


# Path zu PyLucid-root-dir
sys.path.insert(0,"..")
from config import config # PyLucid config file


def connect(config):
    conn_kwargs = {
        "host"      : config["dbHost"],
        "user"      : config["dbUserName"],
        "passwd"    : config["dbPassword"],
        "db"        : config["dbDatabaseName"],
    }
    conn_kwargs["charset"] = USED_ENCODING # ab python-mysqldb v1.2.1-irgendwas :-/
    try:
        connection = MySQLdb.Connect(**conn_kwargs)
    except TypeError, e:
        print "connect error 1:", e
        # Work-a-round für alte MySQLdb Version
        del(conn_kwargs["charset"])
        conn_kwargs["use_unicode"] = True
        try:
            connection = MySQLdb.Connect(**conn_kwargs)
        except Exception, e:
            print "connect error 2:", e
            print "abort!"
            sys.exit()
        else:
            print "Connected with 'use_unicode'."
    except Exception, e:
        print "Connection Error:", e
        print "abort!"
        sys.exit()
    else:
        print "Connected with 'charset=%s'." % USED_ENCODING

    return connection


def set_names(cursor):
    # Funktioniert erst mit MySQL =>v4.1
    print "SET NAMES to %s..." % USED_ENCODING,
    try:
        cursor.execute('SET NAMES %s;', (USED_ENCODING,))
    except Exception, e:
        print "Error:", e
    else:
        print "OK"
    print


def test(connection):
    cursor=connection.cursor()
    set_names(cursor)

    print "Create pickled data...",
    source_test_data = [unichr(i) for i in xrange(0, 256)]
    db_input = pickle.dumps(source_test_data, USED_PICKLE_PROTOCOL)
    print "OK"

    print "Create test table...",
    cursor.execute('CREATE TABLE temp_test (txt LONGBLOB);')
    #~ cursor.execute('CREATE TABLE temp_test (txt LONGTEXT);')
    #~ cursor.execute('CREATE TABLE temp_test (txt LONGBLOB) COLLATE="ascii_bin";')
    print "OK"

    print "SHOW CREATE TABLE:"
    cursor.execute("SHOW CREATE TABLE temp_test;")
    print "-"*40
    print cursor.fetchone()[1]
    print "-"*40

    print "INSERT & SELECT...",
    cursor.execute("INSERT INTO temp_test (txt) VALUES (%s);", (db_input,))
    connection.commit()
    cursor.execute("SELECT * FROM temp_test;")
    db_output = cursor.fetchone()[0]
    db_output = db_output.tostring()
    print "OK"

    print "compare db input with output:",
    if db_input == db_output:
        print "OK"
    else:
        print "Error!"

    print "pickle load...",
    test_data = pickle.loads(db_output)
    print "OK"

    print "compare pickled data:",
    if source_test_data == test_data:
        print "OK"
    else:
        print "Error!"




if __name__ == "__main__":
    connection = connect(config)
    try:
        test(connection)
    finally:
        print "-"*79
        try:
            print "\nDROP TABLE...",
            connection.cursor().execute("DROP TABLE temp_test;")
        except Exception, e:
            print "Error:", e
        else:
            print "OK"

        print "\nClose Connection...",
        connection.close()
        print "OK"

        print "-"*79

    print "END (without Errors)"