#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Erzeugt die Such-Index
"""

__version__="0.0.1"


import sys, re


class SearchIndex:
    """
    Speichert den Index ab.
    Benötigt wird in parseSide() ein Dict der die Seiteninformationen bereit hält
    """

    def __init__( self ):
        self.stopwords      = ("der","die","das")
        self.min_word_len   = 1

        self.index          = {} # Der eigentliche Index
        self.typ            = {} # Speichert die content-Types

    def putWord( self, word, side, pos, typ ):
        """
        ein neues Wort einfügen
        side    - ID/Name der Datei/Seite in dem das Wort vorkommt
        pos     - Position des Wortes
        typ     - Typ (Überschrift, Meta-Tags, normaler Text ect.)
        """
        if not self.index.has_key( word ):
            # Wort noch unbekannt
            self.index[word] = {}

        if not self.index[word].has_key( side ):
            # Datei noch unbekannt
            self.index[word][side] = []

        self.index[word][side].append( (pos,typ) )

    def parseSide( self, side, sidedata ):
        """
        Fügt eine Daten einer Seite in den Index ein
        sidedata ist ein dict welches die geparsten Seiteninhalte bereit hält
        """
        if self.typ == {}:
            keys = sidedata.keys()
            for i in xrange( len(keys) ):
                self.typ[ keys[i] ] = i

        for typ in self.typ:
            pos = 0
            for word in sidedata[typ].split():
                if len(word) <= self.min_word_len:
                    continue
                pos += 1
                self.putWord( word, side, pos, self.typ[typ] )

    ###################
    ## Ausgabe

    def get( self ):
        "Liefert den Index zurück"
        return self.index

    ###################
    ## Debug

    def info1( self ):
        wordlist = self.index.keys()
        print len(wordlist),"Wörter vorhanden"
        print len(self.index),"Bytes ist der Index groß"
        #~ wordlist.sort()
        #~ for word in wordlist:
            #~ print word,":",len( self.index[word] )

    def wordinfo( self, word ):
        if not self.index.has_key( word ):
            print "Wort nicht im Index erhalten!!!"
            return
        print "> [%s] info:" % word
        print self.index[word]

    def dump( self ):
        wordlist = self.index.keys()
        wordlist.sort()
        for word in wordlist:
            print word,":",self.index[word]









#~ print "="*80

#~ MyIndex = index()
#~ MyIndex.parseSide( "TEST", MyParser.get_data() )
#~ MyIndex.parseSide( "TEST2", MyParser.get_data() )
#~ MyIndex.dump()

#~ sys.exit()








if __name__ == "__main__":
    print "Lokaler Test..."
    print "-"*80

    MySide = content()
    MyParser = MetaContentParser()
    MyIndex = index()

    # ID's der vorhanden Seite hohlen
    fileIDs = MySide.getIDs()
    max = 4
    for id in fileIDs:
        #~ max -= 1
        #~ if max == 0: break

        print id,
        SideDict = MySide.getParsedFile( id )
        content = SideDict["content"]

        MyParser.feed( content )
        #~ MyParser.dump()

        MyIndex.parseSide( id, MyParser.get_data() )
        MyParser.close()

    print
    #~ MyIndex.info1()
    MyIndex.save( "wordindex.bin" )
    #~ MyIndex.dump()


    #~ dump( getSideContent() )















