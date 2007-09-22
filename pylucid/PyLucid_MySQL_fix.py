#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Update for PyLucid v0.7.2 tables to the new django version.

changes all wrong 00-00-0000 datetime values to NULL.
django problematic: http://code.djangoproject.com/ticket/443

Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

print "Content-type: text/plain; charset=utf-8\r\n\r\n"
import cgitb;cgitb.enable()

import datetime, os
import MySQLdb

os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"

from django.conf import settings


connection = MySQLdb.Connect(
    host    = settings.DATABASE_HOST,
    user    = settings.DATABASE_USER,
    passwd  = settings.DATABASE_PASSWORD,
    db      = settings.DATABASE_NAME,
)
cursor=connection.cursor()




def fetchall(SQLcommand):
    cursor.execute(SQLcommand)
    return cursor.fetchall()


def catched_execute(SQLcommand):
    try:
        cursor.execute(SQLcommand)
    except Exception, e:
        print "Error:", e
    else:
        print "OK"


def get_all_tables():
    """
    Liste aller Tabellennamen
    """
    table_names = []
    for line in fetchall("SHOW TABLES"):
        table_name = line[0]
        if table_name.startswith(settings.OLD_TABLE_PREFIX):
            table_names.append(table_name)

    return table_names


def get_table_fields(table_name):
    SQLcommand = "SHOW FIELDS FROM %s;" % table_name
    return fetchall(SQLcommand)


def alter_table_field(table_name, field):
    """
    Set "DEFAULT NULL" to a datetime field.
    """
    SQLcommand = (
        "ALTER TABLE %(table)s CHANGE %(field)s %(field)s DATETIME NULL;"
    ) % {
        "table": table_name,
        "field": field,
    }
    print SQLcommand
    print "ALTER TABLE...",
    catched_execute(SQLcommand)


def patch_field_values(table_name, primary_key, field_name):
    """
    Set 00-00-0000 values to a NULL value.
    """
    fields = ",".join([primary_key, field_name])
    SQLcommand = "SELECT %s FROM %s;" % (fields, table_name)

    for current_key, value in fetchall(SQLcommand):
        if isinstance(value, datetime.datetime):
            continue

        SQLcommand = "UPDATE %s SET %s = NULL WHERE %s = %s LIMIT 1;" % (
            table_name, field_name, primary_key, current_key
        )
        print "Update datetime field %s.%s (where %s = %s)..." % (
            table_name, field_name, primary_key, current_key
        ),
        catched_execute(SQLcommand)


if __name__ == "__main__":
    table_names = get_all_tables()
    for table_name in table_names:
        print "---", table_name
        fields = get_table_fields(table_name)
        #~ print fields

        date_fields = []
        primary_key = None
        for field in fields:
            field_name = field[0]
            field_type = field[1]
            field_flag = field[3]
            if field_flag == "PRI":
                primary_key = field_name
            if field_type != "datetime":
                continue

            alter_table_field(table_name, field_name)
            try:
                patch_field_values(table_name, primary_key, field_name)
            except Exception, e:
                print "Error:", e

        print "-"*79

    print "--- END ---"