#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Erzeugt den SearchIndex
"""

__version__="0.0.1"

__history__="""
v0.0.1
    - erste Version
"""


import cgitb;cgitb.enable()
print "Content-type: text/html\n"

# Interne PyLucid-Module einbinden
from PyWebSearch import PyLucidContent, ContentParser, SearchIndex, flatfile


MySide      = PyLucidContent.content()
MyParser    = ContentParser.MetaContentParser()
MyIndex     = SearchIndex.SearchIndex()



def print_process(i, total):
    i += 1
    tresh = total / 10
    if tresh == 0:
        tresh = 1
    if i % tresh == 0:
        print "%3.i%% %4.i/%i" % ( round(float(i)/total*100), i, total)

#~ TestListe = [str(i) for i in xrange(109)]
#~ total = len(TestListe)
#~ for i in xrange(total):
    #~ print_process(i, total)
#~ sys.exit()



# ID's der vorhanden Seite hohlen
fileIDs = MySide.getIDs()

print "<pre>"
total = len( fileIDs )
print "Lese %s Seiten aus der SQL-Datenbank ein und parse diese..." % max

for i in xrange( total ):
    print_process(i, total)

    id = fileIDs[i]

    # Seite aus SQL-Datenbank hohlen
    SideDict = MySide.getParsedFile( id )
    content = SideDict["content"]

    #~ print "-"*80
    #~ print "> Seite mit id:%s - title:%s" % (id, SideDict["title"])
    #~ print content[:100]

    # Wörter extrahieren
    MyParser.feed( content )

    # Seite in index einfügen
    MyIndex.parseSide( id, MyParser.get_data() )
    MyParser.close()

# Index in Datei speichern
flatfile.save_compressed( MyIndex.get() )

print "</pre>"