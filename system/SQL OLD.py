#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Anbindung an die SQL-Datenbank mittels MySQLdb

Benötigt MySQLdb download unter:
http://sourceforge.net/projects/mysql-python/


Bsp.:
-----

db = db()
# Allgemeine SQL-update Funktion
data = {
    "TableFieldName1" : "CellValue1",
    "TableFieldName2" : "CellValue2",
}
db.update(
        table   = "Tablename",
        data    = data,
        where   = ("id", 2 ),
        limit   = 1
    )
# Erzeugt folgenden Befehl:
    UPDATE dbTablePrefix_Tablename
    SET TableFieldName1 = "CellValue1", TableFieldName2 = "CellValue2"
    WHERE id = 2 LIMIT 1;

# Allgemeiner SQL-insert Funktion
data = {
    "TableFieldName1" : "CellValue1",
    "TableFieldName2" : "CellValue2",
}
self.db.insert( "archive", archiv_data )
# Erzeugt folgenden Befehl:
    INSERT INTO dbTablePrefix_Tablename
    ( TableFieldName1, TableFieldName2 )
    VALUES ( "CellValue1", "CellValue2"  );


ToDo
----
    * update und insert benutzen das SQLdb-Escapeing. Die select-Funktion allerdings
      noch nicht!
"""

__version__="0.0.3"

__history__="""
v0.0.3
    - Allgemeine SQL insert und update Funktion eingefügt
    - SQL-where-Parameter kann nun auch meherere Bedingungen haben
v0.0.2
    - Allgemeine select-SQL-Anweisung
    - Fehlerausgabe bei fehlerhaften SQL-Anfrage
v0.0.1
    - erste Release
"""

# Python-Basis Module einbinden
import sys


try:
    import MySQLdb as DBlib
except ImportError:
    print "Content-type: text/html\n"
    print "<h1>Error</h1>"
    print "<h3>MySQLdb import error! Modul 'python-mysqldb' not installed???</h3>"
    sys.exit(0)


# Interne PyLucid-Module einbinden
from config import dbconf



class db:
    """
    Klasse, die nur allgemeine SQL-Funktionen beinhaltet
    """
    def __init__( self ):
        self.connect()

    def connect( self ):
        # Erstellt eine Connection zur mySQL-DB
        try:
            self.connection = DBlib.connect(
                dbconf["dbHost"],
                dbconf["dbUserName"],
                dbconf["dbPassword"],
                dbconf["dbDatabaseName"]
            )
            self.cursor = self.connection.cursor()
        except Exception, e:
            print "Content-type: text/html\n"
            print "<pre>"
            print "Can't connect to SQL-DB:", e
            #~ import traceback
            #~ import StringIO
            #~ tb = StringIO.StringIO()
            #~ traceback.print_exc(file=tb)
            #~ print tb.getvalue()
            print "="*80
            print "dbHost:",dbconf["dbHost"]
            #~ print "dbUserName:",dbconf["dbUserName"]
            print "dbDatabaseName:",dbconf["dbDatabaseName"]
            print "="*80
            print "Please check DB-settings in /PyLucid/system/config.py !!!"
            print "</pre>"
            sys.exit(1)

    def get( self, SQLcommand ):
        "kombiniert execute und fetchall"
        self.cursor.execute(
                SQLcommand.replace("%(dbTablePrefix)s", dbconf["dbTablePrefix"])
            )
        return self.cursor.fetchall()

    def insert( self, table, data ):
        """
        Vereinfachter Insert, per dict
        data ist ein Dict, wobei die SQL-Felder den Key-Namen im Dict entsprechen muß!
        """
        items   = data.keys()
        values  = data.values()

        SQLcommand = "INSERT INTO `%(dbTablePrefix)s%(table)s` ( %(items)s ) VALUES ( %(values)s );" % {
                "dbTablePrefix" : dbconf["dbTablePrefix"],
                "table"         : table,
                "items"         : ",".join( items ),
                "values"        : ",".join( ["%s"]*len(values) ) # Platzhalter für SQLdb-escape
            }
        if len( values ) == 1:
            self.cursor.execute( SQLcommand, (values[0],) )
        else:
            self.cursor.execute( SQLcommand, tuple( values ) )

    def update( self, table, data, where, limit=None ):
        """
        Vereinfachte SQL-update Funktion
        """
        items   = data.keys()
        values  = data.values()

        if not limit == None:
            limit = "LIMIT %s" % limit
        else:
            limit = ""

        SQLcommand = "UPDATE %(table)s SET %(set)s WHERE %(where)s %(limit)s;" % {
                "table"     : dbconf["dbTablePrefix"] + table,
                "set"       : ",".join( [str(i)+"=%s" for i in items] ),
                "where"     : "%s='%s'" % (where[0],where[1]),
                "limit"     : limit
            }
        if len( values ) == 1:
            self.cursor.execute( SQLcommand, (values[0],) )
        else:
            self.cursor.execute( SQLcommand, tuple( values ) )

    def SQLescapelist( self, items ):
        itemlist = []
        for i in items:
            if type(i) != str: i = str( i )
            itemlist.append( DBlib.string_literal(i) )

        return ",".join( itemlist )

    def select( self, select_items, from_table, where=None, order=None, limit=None, debug=False ):
        """
        Allgemeine SQL-SELECT Anweisung
        where, order und limit sind optional
        mit debug=True wird das SQL-Kommando generiert, ausgegeben und sys.exit()

        where
        -----
        Die where Klausel ist ein wenig special.

        einfache where Klausel:
        where=("parent",0) ===> WHERE `parent`="0"

        mehrfache where Klausel:
        where=[("parent",0),("id",0)] ===> WHERE `parent`="0" and `id`="0"
        """
        #~ debug = True

        SQLcommand = "SELECT " + ",".join( select_items )
        SQLcommand += " FROM `%s%s`" % ( dbconf["dbTablePrefix"], from_table )

        if where != None:
            if type( where[0] ) == type(""):
                # es ist nur eine where-Regel vorhanden.
                # Damit die folgenden Anweisungen auch gehen
                where = [ where ]

            where_string = []
            for item in where:
                if type(item[1]) == int:
                    where_string.append( '`%s`=%s' % (item[0],item[1]) )
                else:
                    where_string.append( '`%s`="%s"' % (item[0],item[1]) )
            #~ where_string = ['`%s`="%s"' % (i[0],i[1]) for i in where]
            where_string = " and ".join( where_string )

            SQLcommand += ' WHERE %s' % where_string

        if order != None:
            SQLcommand += " ORDER BY `%s` %s" % order

        if limit != None:
            SQLcommand += " LIMIT %s,%s" % limit

        if debug == True:
            print "Content-type: text/html\n"
            print "<pre> (debug) SQL-command:"
            print "-"*80
            print SQLcommand
            print "-"*80

        #~ print SQLcommand
        RAWresult = self.get( SQLcommand )

        if debug == True:
            print RAWresult
            sys.exit()


        if select_items == "*":
            # Spezielle Auswertung bei "SELECT *"-Anfragen
            # Erstellt ein Dict mit den Namen der Tabellen-Felder

            RAWresult = RAWresult[0]
            #~ print ">>>",RAWresult
            #~ self.dump_select_result( RAWresult )

            descriptions = self.cursor.description
            #~ print descriptions

            result = {}

            for i in xrange( len(RAWresult) ):
                result[ descriptions[i][0] ] = RAWresult[i]
                #~ print i,descriptions[i][0],RAWresult[i]# [:10]

            return result

        result = []
        itemlen = len(select_items)
        for line in RAWresult:
            temp = {}
            for i in xrange( itemlen ):
                temp[ select_items[i] ] = line[i]
            result.append( temp )

        return result

    def dump_select_result( self, result ):
        for line in result:
            print line

    def close( self ):
        self.connection.close()


    #################################################################
    # Spezielle lucidCMS Funktionen, die von Modulen gebraucht werden

    def side_id_by_name( self, page_name ):
        "Liefert die Side-ID anhand des >page_name< zurück"
        result = self.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ("name",page_name)
            )
        if result == []:
            return False

        if result[0].has_key("id"):
            return result[0]["id"]
        else:
            return False

    def side_name_by_id( self, page_id ):
        "Liefert den Page-Name anhand der >page_id< zurück"
        return self.select(
                select_items    = ["name"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["name"]

    def parentID_by_name( self, page_name ):
        """
        liefert die parend ID anhand des Namens zur���
        """
        # Anhand des Seitennamens wird die aktuelle SeitenID und den ParentID ermittelt
        return self.select(
                select_items    = ["id","parent"],
                from_table      = "pages",
                where           = ("name",page_name)
            )[0]["parent"]

    def side_title_by_id( self, page_id ):
        "Liefert den Page-Title anhand der >page_id< zurück"
        return self.select(
                select_items    = ["title"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["title"]

    def side_template_by_id( self, page_id ):
        "Liefert den Inhalt des Template-ID und Templates für die Seite mit der >page_id< zurück"
        template_id = self.select(
                select_items    = ["template"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["template"]
        page_template = self.select(
                select_items    = ["content"],
                from_table      = "templates",
                where           = ("id",template_id)
            )[0]["content"]

        return page_template

    def side_style_by_id( self, page_id ):
        "Liefert die CSS-ID und CSS für die Seite mit der >page_id< zurück"
        CSS_id = self.select(
                select_items    = ["style"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["style"]
        CSS_content = self.select(
                select_items    = ["content"],
                from_table      = "styles",
                where           = ("id",CSS_id)
            )[0]["content"]

        return CSS_content

    def get_page_data_by_id( self, page_id ):
        "Liefert die Daten zum Rendern der Seite zurück"
        return self.select(
                select_items    = ["content", "markup"],
                from_table      = "pages",
                where           = ("id", page_id)
            )[0]

    def page_items_by_id( self, item_list, page_id ):
        "Allgemein: Daten zu einer Seite"
        return self.select(
                select_items    = item_list,
                from_table      = "pages",
                where           = ("id", page_id)
            )[0]

    def preferences( self, section, varName ):
        "Liefert Daten aus der Preferences-Tabelle anhand von >section< und >varName< zurück"
        return self.select(
                select_items    = ["name", "description", "value", "type"],
                from_table      = "preferences",
                where           = [("section",section), ("varName",varName)]
            )[0]



    ##----------------------------------------
    ## InterneSeiten

    def get_internal_page( self, pagename ):
        pagename = "__%s__" % pagename
        try:
            return self.select(
                    select_items    = ["content", "markup", "ownerID"],
                    from_table      = "pages",
                    where           = ("name", pagename)
                )[0]
        except:
            print "Content-type: text/html\n"
            print "<h1>Error!</h1>"
            print "<h3>Can't find internal Page '%s' in DB!</h3>" % pagename
            print "<p>Did you run 'install_PyLucid.py' ???</p>"
            sys.exit(1)

    def get_internal_group_id( self ):
        """
        Liefert die ID der internen PyLucid Gruppe zurück
        Wird verwendet für interne Seiten!
        """
        internal_group_name = "PyLucid_internal"
        return self.select(
                select_items    = ["id"],
                from_table      = "groups",
                where           = ("name", internal_group_name)
            )[0]["id"]




    ##----------------------------------------
    ## Userverwaltung

    def add_User( self, name, realname, email, password, admin ):
        "Hinzufügen der Userdaten in die normale lucidCMS-Tabelle"
        SQLcommand  = "INSERT INTO `%susers`" % dbconf["dbTablePrefix"]
        SQLcommand += " ( name,realName,email,password,admin )"
        SQLcommand += " VALUES ( %s,%s,%s,%s,%s );"
        self.cursor.execute( SQLcommand, (name, realname, email, password, admin) )

    def normal_login_userdata( self, username ):
        "Userdaten die bei einem normalen Login benötigt werden"
        return self.select(
                select_items    = ["id", "password", "admin"],
                from_table      = "users",
                where           = ("name", username)
            )[0]

    def add_md5_User( self, name, realname, email, pass1, pass2, admin ):
        "Hinzufügen der Userdaten in die PyLucid's JD-md5-user-Tabelle"
        SQLcommand  = "INSERT INTO `%smd5users`" % dbconf["dbTablePrefix"]
        SQLcommand += " ( name, realname, email, pass1, pass2, admin )"
        SQLcommand += " VALUES ( %s,%s,%s,%s,%s,%s );"
        self.cursor.execute( SQLcommand, (name, realname, email, pass1, pass2, admin) )

    def md5_login_userdata( self, username ):
        "Userdaten die beim JS-md5 Login benötigt werden"
        return self.select(
                select_items    = ["id", "pass1", "pass2", "admin"],
                from_table      = "md5users",
                where           = ("name", username)
            )[0]





if __name__ == "__main__":
    print ">Loaker Test:"
    db = db()

    result = db.select(
            select_items    = ["id","name"],
            from_table      = "pages",
            where           = ("parent",0)#,debug=1
        )
    db.dump_select_result( result )

    print "="*80

    result = db.select(
            select_items    = ["id","name"],
            from_table      = "pages",
            where           = [("parent",0),("id",1)]#,debug=1
        )
    db.dump_select_result( result )







