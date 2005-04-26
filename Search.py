#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Führt eine Suche im SearchIndex durch
"""

__version__="0.0.1"

__history__="""
v0.0.1
    - erste Version (Trefferliste hat noch keine Gewichtung!)
"""

import os
if os.environ.has_key("SERVER_SIGNATURE"):
    import cgitb;cgitb.enable()

print "Content-type: text/html\n"
print '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'

# Python-Basis Module einbinden
import sys,os,time

# Interne PyLucid-Module einbinden
from system import CGIdata, sessiondata, config
from system.lucid_sql_access import lucid_sql
from PyWebSearch import Search_the_Index
from PyWebSearch.flatfile import access


SuchForm = '''
<form method="post" action="%(url)s">
<p>
Suche: <input type="text" name="SearchString" value="%(startvalue)s" /><input type="submit" value="Finden" />
</p>
</form>
'''

ScriptURL = "http://www.jensdiemer.de/cgi-bin/PyLucid/Search.py"
backURL = "/"
hit_link = '<a href="http://cms.jensdiemer.de/index.php?%(name)s" target="_top">%(title)s</a>'





class search:
    def __init__( self ):
        if not os.environ.has_key("SERVER_SIGNATURE"):
            search_string = "Jens Diemer 021111"
            #~ search_string = "keinErgebniss"
            print "Lokaler Test!"
            print "suche nach '%s'" % search_string
        else:
            CGIdata.get()

            if not sessiondata.cgi.data.has_key("SearchString"):
                # Aufruf mit ohne/falschen Parametern -> Suchmaske anzeigen
                self.print_form( "" )
                sys.exit()

            search_string = sessiondata.cgi.data["SearchString"][:50]
            self.log( "SearchString: [%s]" % search_string )

        MyIndex = access()
        MySearch = Search_the_Index.Search( MyIndex, search_string )

        self.print_form( MySearch.get_search_words() )

        result = MySearch.make_search()

        self.print_result( result )

    def print_form( self, startvalue ):
        print SuchForm % {
            "url"           : ScriptURL,
            "backurl"       : backURL,
            "startvalue"    : startvalue
        }

    def print_result( self, result ):
        db = lucid_sql()
        itemlist = ["title","name"]

        print "<ul>"
        for SideID in result:
            content = db.page_item_by_id( SideID, itemlist )

            name = content["name"]
            title = content["title"]

            if title == None: title = name

            print '<li>'
            print hit_link % {
                "name"  : name,
                "title" : title
            }
            print '</li>'
        print "</ul>"


    def log( self, txt ):
        from socket import getfqdn
        REMOTE_ADDR = os.environ["REMOTE_ADDR"]
        IPInfo      = getfqdn( REMOTE_ADDR )

        LogDatei = config.LogDatei % "Search"

        text="%s %s %s - %s\n" % (
                time.strftime("%d.%m.%Y %H:%M.%S"),
                REMOTE_ADDR,
                IPInfo,
                txt
            )

        l = open(LogDatei,"a")
        l.write(text)
        l.close()



if __name__ == "__main__":
    search()




















