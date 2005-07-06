#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Anbindung an die SQL-Datenbank
"""

__version__="0.0.4"

__history__="""
v0.0.4
    - SQL-wrapper ausgelagert in mySQL.py
v0.0.3
    - Allgemeine SQL insert und update Funktion eingefügt
    - SQL-where-Parameter kann nun auch meherere Bedingungen haben
v0.0.2
    - Allgemeine select-SQL-Anweisung
    - Fehlerausgabe bei fehlerhaften SQL-Anfrage
v0.0.1
    - erste Release
"""


# Interne PyLucid-Module einbinden
from mySQL import mySQL
from config import dbconf
import lucid_tools



class db( mySQL ):
    """
    Erweitert den allgemeinen SQL-Wrapper (mySQL.py) um
    spezielle PyLucid-Funktionen.
    """
    def __init__( self ):
        #~ print "Content-type: text/html\n"
        #~ print "<h2>Connecte zur DB!</h2>"
        #~ import inspect
        #~ for line in inspect.stack(): print line,"<br>"

        try:
            # SQL connection aufbauen
            mySQL.__init__( self,
                    host    = dbconf["dbHost"],
                    user    = dbconf["dbUserName"],
                    passwd  = dbconf["dbPassword"],
                    db      = dbconf["dbDatabaseName"],
                    #~ unicode = 'utf-8'
                    #~ use_unicode = True
                )
        except Exception, e:
            print "Content-type: text/html\n"
            print "<h1>PyLucid - Error</h1>"
            print "<h2>Can't connect to SQL-DB: '%s'</h2>" % e
            import sys
            sys.exit()

        # Table-Prefix for all SQL-commands:
        self.tableprefix = dbconf["dbTablePrefix"]

    def type_error( self, itemname, item ):
        print "Content-type: text/html\n"
        print "<h1>SQL Error:</h1>"
        print "<h2>%s is not String!</h2>" % itemname
        import cgi
        print "<p>It's %s<br/>" % cgi.escape( str( type(item) ) )
        print "Check SQL-Table settings!</p>"
        import sys
        sys.exit()

    #################################################################
    # Spezielle lucidCMS Funktionen, die von Modulen gebraucht werden

    def get_page_data( self, page_id ):
        "Holt die nötigen Informationen über die aktuelle Seite"

        side_data = self.select(
                select_items    = [
                        "name", "title", "content", "markup", "lastupdatetime","keywords","description"
                    ],
                from_table      = "pages",
                where           = ( "id", page_id )
            )[0]

        # Datum wandeln
        side_data["lastupdatetime"] = lucid_tools.date( side_data["lastupdatetime"] )

        side_data["template"] = self.side_template_by_id( page_id )

        if side_data["title"] == None:
            side_data["title"] = side_data["name"]

        if type(side_data["content"]) != str:
            self.type_error( "Sidecontent", side_data["content"] )

        #~ print side_data
        return side_data

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

        if type(page_template) != str:
            self.type_error( "Template-Content", page_template )

        return page_template

    def get_preferences( self ):
        "Die Preferences aus der DB holen. Wird verwendet in config.readpreferences()"
        return self.select(
                select_items    = ["section", "varName", "value"],
                from_table      = "preferences",
            )

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
        data = self.select(
                select_items    = ["content", "markup"],
                from_table      = "pages",
                where           = ("id", page_id)
            )[0]
        if data["content"] == None:
            # Wenn eine Seite mit lucidCMS frisch angelegt wurde und noch kein
            # Text eingegeben wurde, ist "content" == None
            data["content"] = ""
        return data

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
        #~ pagename = "__%s__" % pagename
        try:
            return self.select(
                    select_items    = ["content", "markup"],
                    from_table      = "pages_internal",
                    where           = ("name", pagename)
                )[0]
        except:
            print "Content-type: text/html\n"
            print "<h1>Error!</h1>"
            print "<h3>Can't find internal Page '%s' in DB!</h3>" % pagename
            print "<p>Did you run 'install_PyLucid.py' ???</p>"
            import sys
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

    # Prints all SQL-command:
    db.debug = True

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







