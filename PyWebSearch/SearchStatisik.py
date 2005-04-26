#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Liefert Informationen zur Such-Index-Datei
"""

__version__="0.0.1"



#~ import cgitb;cgitb.enable()
import sys, shelve, bz2, pickle, anydbm

class seachindex:
    def __init__( self, indexfile ):
        self.index = shelve.open( indexfile, "r" )

    def info1( self ):
        wordlist = self.index.keys()
        wordlist.sort()
        for word in wordlist:
            print word

class compress:
    "Index Komprimieren"
    def __init__( self, indexfile, compresslevel = 9 ):
        self.index = shelve.open( indexfile, "r" )
        self.compresslevel = compresslevel

    def compress( self, outfile ):
        outfile = anydbm.open( outfile, "n" )

        for word in self.index.keys():
            data = pickle.dumps( self.index[word] )
            outfile[word] = bz2.compress( data, self.compresslevel )

    def compress1( self, outfile ):
        print "komprimiere..."

        outfile = anydbm.open( outfile, "n" )
        wordlist = self.index.keys()
        max = len(wordlist)

        threshold = max / 10
        status = 0
        perc = 0
        for i in xrange( max ):
            status += 1
            if status >= threshold:
                perc += 10
                print perc,"%"
                status = 0

            word = wordlist[i]
            worddata = self.index[word]

            data = pickle.dumps( worddata )
            outfile[word] = bz2.compress( data, self.compresslevel )


class compaccess:
    "Auf komprimierte Daten zugreifen"
    def __init__( self, compressedIndexFile ):
        self.index = anydbm.open( compressedIndexFile, "r" )

    def get( self, word ):
        compresseddata = self.index[word]
        data = bz2.decompress( compresseddata )
        return pickle.loads( data )




if __name__ == "__main__":
    print "Lokaler Test..."
    print "-"*80

    #~ MyIndex = seachindex( "wordindex.bin" )
    #~ MyIndex.info1()

    "Index Komprimieren"
    #~ compress( "wordindex.bin" ).compress( "wordindexcompressed.bin" )

    "Auf komprimierte Daten zugreifen"
    MyIndex = compaccess( "wordindexcompressed.bin" )
    print MyIndex.get("Jens")
    print MyIndex.get("python")

    sys.exit()