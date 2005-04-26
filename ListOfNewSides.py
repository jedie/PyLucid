#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert eine Liste der "letzten Änderungen"
"""

__version__="0.0.2"

__history__="""
v0.0.2
    - Anpassung an neue SQL.py Version
    - Nur Seiten Anzeigen, die auch permitViewPublic=1 sind (also öffentlich)
v0.0.1
    - erste Version
"""



#~ import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import re

print "Content-type: text/html\n"

# Interne PyLucid-Module einbinden
from system import SQL, lucid_tools


def getNewSides():
    db = SQL.db()
    result = db.select(
        select_items    = [ "title", "name", "lastupdatetime" ],
        from_table      = "pages",
        where           = ( "permitViewPublic", 1 ),
        order           = ( "lastupdatetime", "DESC" ),
        limit           = ( 0, 5 )
    )
    return result

def printNewSides( SQLresult ):
    print "<ul>"

    for item in SQLresult:
        linkTitle   = item["title"]
        linkName    = item["name"]

        if linkTitle == None:
            # Eine Seite muß nicht zwingent ein Title haben
            linkTitle = item["name"]

        line = '%(date)s - <a href="?%(Name)s">%(Title)s</a>' % {
            "Name"  : linkName,
            "Title" : linkTitle,
            "date"  : lucid_tools.date( item["lastupdatetime"] )
        }
        print "<li>%s</li>" % line

    print "</ul>"



if __name__ == "__main__":
    printNewSides( getNewSides() )












