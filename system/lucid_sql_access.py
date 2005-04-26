#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Fertige Konstrukte zum Auslesen der lucidCMS-Datenbank
"""

__version__="0.0.1"

import sys

import config, preferences, SQL


class lucid_sql( SQL.db ):

    def page_item_by_id( self, SideID, itemlist ):
        """
        Liefert anhand der id ein dict mit den item's zurück
        itemlist ist...
        """

        select_item_string = self.joinSQLlist( itemlist )

        SQLcommand = "SELECT %(items)s FROM `%(prefix)spages` WHERE `id`=%(id)d" % {
            "items"     : select_item_string,
            "prefix"    : config.dbconf["dbTablePrefix"],
            "id"        : SideID
        }

        # SQL-Datenbank abfragen
        RAWdata = self.get( SQLcommand )[0]

        # Ergebniss in ein Dict verpacken
        result = {}
        for n in xrange( len(itemlist) ):
            result[ itemlist[n] ] = RAWdata[n]

        return result

    def joinSQLlist( self, itemlist ):
        "Konvertiert eine Liste in einen String für eine SQL Abfrage"
        return ",".join( ["`%s`" % i for i in itemlist] )


if __name__ == "__main__":
    MyDB = lucid_sql()

    itemlist = [ "title", "markup", "lastupdatetime" ]
    print MyDB.page_item_by_id( 3, itemlist )