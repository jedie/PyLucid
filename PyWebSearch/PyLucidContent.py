#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Anbindung an die SQL-Datenbank von lucidCMS
Nutzt PyLucid!
"""

__version__="0.0.1"


import sys, os

PyLucidBaseDir = os.path.normpath( os.path.join( os.getcwd( ), ".." ) )
sys.path.append( PyLucidBaseDir )

from system import config, preferences, SQL
from textile import textile


class content:
    def __init__( self ):
        self.db = SQL.db()

    def getIDs( self ):
        SQLcommand = "SELECT `id` FROM `%spages`" % config.dbconf["dbTablePrefix"]
        idlist = []
        for id in self.db.get( SQLcommand ):
            idlist.append( int(id[0]) )
        return idlist

    def content_by_id( self, SideID ):
        "Liefert ein dict mit den Seiteninformationen anhand der ID zurück"

        SQLcommand = "SELECT `title`,`name`,`content`,`markup` FROM `%spages` WHERE `id`=%d" % (
            config.dbconf["dbTablePrefix"],
            SideID
        )

        RAWdata = self.db.get( SQLcommand )[0]

        return {
            "title"     : RAWdata[0],
            "name"      : RAWdata[1],
            "content"   : RAWdata[2],
            "markup"    : RAWdata[3]
        }

    def markup( self, SideDict ):
        if SideDict["markup"] == "textile":
            SideDict["content"] = textile.textile( SideDict["content"] )
        return SideDict

    def getParsedFile( self, id ):
        return self.markup( self.content_by_id( id ) )

    def dump( self, SQLresult ):
        for line in SQLresult:
            linkTitle   = line[0]
            linkName    = line[1]
            content     = line[2]
            print "-"*80
            print ">",linkTitle
            txt = content[:200]
            print txt
            print re.findall(r"([\wäöüßÄÖÜ]+)", txt )



if __name__ == "__main__":
    if os.environ.has_key("SERVER_SIGNATURE"):
        import cgitb;cgitb.enable()
        print "Content-type: text/plain\n"

    print "Lokaler Test..."
    print "-"*80

    MySide = content()

    # ID's der vorhanden Seite hohlen
    fileIDs = MySide.getIDs()
    print "Seiten ID-Liste:"
    print fileIDs
    print

    fileIDs = [16,17,21,39]

    max = 5
    print "Ausschnitt aus der ersten %s Seiten" % max
    for id in fileIDs:
        max -= 1
        if max == 0: break

        SideDict = MySide.getParsedFile( id )
        content = SideDict["content"]

        print "-"*80
        print "> Seite mit id:%s - title:%s" % (id, SideDict["title"])
        print content[:100]

