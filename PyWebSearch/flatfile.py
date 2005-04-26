#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Verwaltet den erstellten Such-Index in einer Datei.
"""

__version__="0.0.1"

import os
if os.environ.has_key("SERVER_SIGNATURE"):
    import cgitb;cgitb.enable()
import sys, shelve, pickle, anydbm

try:
    # bz2 gibt es erst in Python 2.3
    from bz2 import compress, decompress
except ImportError:
    from zlib import compress, decompress



from system import config



def save_compressed( index, compresslevel = 9 ):
    "Index Komprimiert abspeichern"

    outfile = anydbm.open( config.search.indexDBfile, "n" )
    wordlist = index.keys()
    max = len(wordlist)

    print "komprimiere %s Datensätze (Wörter)..." % max

    threshold = max / 10
    status = 0
    perc = 0
    for i in xrange( max ):
        status += 1
        if status >= threshold:
            perc += 10
            print "%s%% | %s von %s" % ( perc, i, max )
            status = 0

        word = wordlist[i]

        data = pickle.dumps( index[word] )
        outfile[word] = compress( data, compresslevel )

    outfile.close()





class access:
    "Auf komprimierte Daten zugreifen"
    def __init__( self ):
        self.index = anydbm.open( config.search.indexDBfile, "r" )

    def __getitem__( self, word ):
        compresseddata = self.index[word]
        data = decompress( compresseddata )
        return pickle.loads( data )

    def has_key(self, key):
        return self.index.has_key( key )




if __name__ == "__main__":
    print "Lokaler Test..."
    print "-"*80

    #~ MyIndex = seachindex()
    #~ MyIndex.info1()

    "Index Komprimieren"
    #~ compress( "wordindex.bin" ).compress( "wordindexcompressed.bin" )

    "Auf komprimierte Daten zugreifen"
    MyIndex = compaccess( "wordindexcompressed.bin" )
    print MyIndex.get("Jens")
    print MyIndex.get("python")

    sys.exit()