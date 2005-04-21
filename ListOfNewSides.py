#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Generiert eine Liste der "letzten Änderungen"
"""

__version__="0.0.1"



#~ import cgitb;cgitb.enable()
import re

print "Content-type: text/html\n"

from system import config, preferences, SQL, lucid_tools


def getNewSides():
    dbTablePrefix = config.dbconf["dbTablePrefix"]

    #~ print dbTablePrefix
    #~ print config.dbconf

    SQLcommand = """SELECT `title`,`name`,`lastupdatetime` FROM `%spages` ORDER BY `lastupdatetime` DESC
    LIMIT 0 , 5""" % dbTablePrefix

    db = SQL.db()
    db.execute( SQLcommand )
    result = db.fetchall()

    return result

def printNewSides( SQLresult ):
    print "<ul>"
    #~ print SQLresult
    for line in SQLresult:
        linkTitle   = line[0]
        linkName    = line[1]
        date        = lucid_tools.date( line[2] )

        if linkTitle == None:
            # Eine Seite muß nicht zwingent ein Title haben
            linkTitle = linkName

        line = '%(date)s - <a href="?%(Name)s">%(Title)s</a>' % {
            "Name" : linkName,
            "Title" : linkTitle,
            "date" : date
        }
        print "<li>%s</li>" % line
    print "</ul>"



if __name__ == "__main__":
    printNewSides( getNewSides() )












