#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Ein Test des Indexes
"""

import urllib2

from ContentParser import MetaContentParser
from SearchIndex import SearchIndex


TestURLs = [
        "http://www.heise.de",
        "http://www.heise.de/security/",
        "http://www.heise.de/ct/",
        "http://www.heise.de/tp/"
    ]

MyParser = MetaContentParser()
MyIndex = SearchIndex()

for url in TestURLs:
    print "rufe [%s] ab..." % url,
    c = urllib2.urlopen( url )
    HTMLside = c.read()
    c.close()
    print "OK"


    print "Parse Daten...",
    MyParser.feed( HTMLside )
    print "OK"

    #~ print "-"*80
    #~ MyParser.dump()

    MyIndex.parseSide( id, MyParser.get_data() )
    MyParser.close() # Parser rücksetzten

MyIndex.info1()
MyIndex.wordinfo( "Impressum" )
MyIndex.wordinfo( "News" )
MyIndex.wordinfo( "XP" )

