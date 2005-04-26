#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Führt eine Suche über den Index durch
"""

__version__="0.0.1"




import sys, os, re


try:
    set
except NameError:
    # set() aus Python 2.4.1 Quellentexten importieren
    from system.sets import Set as set


from PyWebSearch import PyLucidContent


class Search:
    def __init__( self, index, search_string ):
        self.index = index

        # Such-String in Liste wandeln
        self.search_words = self.make_search_words( search_string )

    def make_search( self ):
        "Führt die eigentliche such durch"

        # Jedes Wort abfragen
        search_data = self.get_data()

        # ID-Liste der Dateien, bei dem jedes Suchwort vorkommt
        return self.and_search( search_data )

    def get_search_words( self ):
        return " ".join( self.search_words )

    def make_search_words( self, search_string ):
        "Wörter aus der Suchanfarge-String extrahieren"
        search_words = re.findall(r"([\wäöüßÄÖÜ]+)", search_string )
        if len(search_words) == 0:
            self.error()
        return search_words

    def get_data( self ):
        "Daten jedes Such-Wort aus der DB hohlen"
        result = {}
        for word in self.search_words:
            if self.index.has_key( word ):
                result[word] = self.index[word]
            else:
                self.noresult()
        return result

    def and_search( self, search_data ):
        "Dateien finden, in der alle Suche-Wörter vorkommen"
        filelist = search_data.values()

        result = set( filelist[0] )
        for i in xrange( 1,len(filelist) ):
            result = result & set( filelist[i] )
        return list( result )

    def noresult( self ):
        print "Keine Seite gefunden!"
        sys.exit()

    def error( self ):
        print "Fehler!"
        sys.exit()



if __name__ == "__main__":
    from PyWebSearch.flatfile import access
    MyIndex = access( "files/SearchIndex.bin" )

    search_string = "Jens Diemer 021111"
    Search( MyIndex, search_string )#.get_result()

    print "="*80

    search_string = "021111"
    Search( MyIndex, search_string )#.get_result()

