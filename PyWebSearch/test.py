#!/usr/bin/python
# -*- coding: UTF-8 -*-

#~ import cgitb;cgitb.enable()
from sets import Set as set

print "Content-type: text/html\n"


def and_list( data ):
    filelist = data.values()

    print "Listen anzeigen:"
    for i in filelist: print i
    print "-"*80

    result = set( filelist[0] )
    for i in xrange( 1,len(filelist) ):
        result = result & set( filelist[i] )
    return list( result )


data = {
    "eins" : [36, 37, 38, 39],
    "zwei" : [36, 37],
    "drei" : [32, 33, 34, 35, 36, 37]
}

print "<pre>"
result = and_list( data )
print "Ergebnis:", result

print "-"*80

result = and_list( {"nureins":[1,2,3]} )
print "Ergebnis:", result