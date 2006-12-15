#!/usr/bin/python
# -*- coding: UTF-8 -*-

print "-==[ set the reset timer in the DEMO database ]==-\n"

"""
Für das Plugin "demo_reset_time"

Um in der DEMO Seite von PyLucid einen reset-Counter einbauen zu können,
muss in die Datenbank eintragen sein, wann der nächste reset sein wird.
"""

# Angabe, in wieviel Minuten der nächste reset stattfindet:
RESET_MIN = 30

import sys, datetime, MySQLdb


# In welcher Zeit, wird ein reset wieder ausgelöst?
delta = datetime.timedelta(minutes=RESET_MIN)
# Absoluten Zeitpunkt ausrechnen:
now = datetime.datetime.now()
next_reset_time = now + delta


sys.path.insert(0,"..") # PyLucid root
from config import config # PyLucid config file

dbTablePrefix = config["dbTablePrefix"]

connection = MySQLdb.Connect(
    host    = config["dbHost"],
    user    = config["dbUserName"],
    passwd  = config["dbPassword"],
    db      = config["dbDatabaseName"],
)
cursor=connection.cursor()

try:
    print "create demo_data table...",
    try:
        cursor.execute(
            "CREATE TABLE %sdemo_data (reset_time datetime);" % dbTablePrefix
        )
    except Exception, e:
        print "Error:", e
    else:
        print "OK"
        
    print "insert current reset time...",
    SQLcommand = (
        "INSERT INTO %sdemo_data (reset_time) VALUES (%%s);"
    ) % dbTablePrefix
    try:
        cursor.execute(SQLcommand,(next_reset_time,))
    except Exception, e:
        print "Error:", e
    else:
        print "OK"
finally:
    print "\nClose Connection...",
    connection.close()
    print "OK"