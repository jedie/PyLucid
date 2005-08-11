#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Anbindung an die SQL-Datenbank
"""

__version__="0.0.6"

__history__="""
v0.0.6
    - Fehlerausgabe geändert
    - Fehlerausgabe bei side_template_by_id() wenn Template nicht existiert.
v0.0.5
    - NEU: Funktionen für das editieren von Styles/Templates
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

    def _error( self, type, txt ):
        print "Content-type: text/html\n"
        print "<h1>SQL error</h1>"
        print "<h1>%s</h1>" % type
        print "<p>%s</p>" % txt
        print
        import sys
        sys.exit()

    def _type_error( self, itemname, item ):
        import cgi
        self._error(
            "%s is not String!" % itemname,
            "It's %s<br/>Check SQL-Table settings!" % cgi.escape( str( type(item) ) )
        )

    #_____________________________________________________________________________
    # Spezielle lucidCMS Funktionen, die von Modulen gebraucht werden

    def get_side_data( self, page_id ):
        "Holt die nötigen Informationen über die aktuelle Seite"

        side_data = self.select(
                select_items    = [
                        "name", "title", "content", "markup", "lastupdatetime","keywords","description"
                    ],
                from_table      = "pages",
                where           = ( "id", page_id )
            )[0]

        side_data["template"] = self.side_template_by_id( page_id )

        if side_data["title"] == None:
            side_data["title"] = side_data["name"]

        if type(side_data["content"]) != str:
            self._type_error( "Sidecontent", side_data["content"] )

        return side_data

    def side_template_by_id( self, page_id ):
        "Liefert den Inhalt des Template-ID und Templates für die Seite mit der >page_id< zurück"
        template_id = self.select(
                select_items    = ["template"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["template"]

        try:
            page_template = self.select(
                    select_items    = ["content"],
                    from_table      = "templates",
                    where           = ("id",template_id)
                )[0]["content"]
        except Exception, e:
            self._error(
                "Can't get Template",
                "Page-ID: %s, Template-ID: %s" % (page_id, template_id)
            )

        if type(page_template) != str:
            self._type_error( "Template-Content", page_template )

        return page_template

    #~ def get_preferences( self ):
        #~ "Die Preferences aus der DB holen. Wird verwendet in config.readpreferences()"
        #~ value = self.select(
                #~ select_items    = ["section", "varName", "value"],
                #~ from_table      = "preferences",
            #~ )



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

    def get_all_preferences( self ):
        """
        Liefert Daten aus der Preferences-Tabelle
        wird in PyLucid_system.preferences verwendet
        """
        return self.select(
                select_items    = ["section", "varName", "value"],
                from_table      = "preferences",
            )


    def get_page_link_by_id( self, page_id ):
        """ Generiert den absolut-Link zur Seite """
        data = []
        while page_id != 0:
            result = self.select(
                    select_items    = ["name","parent"],
                    from_table      = "pages",
                    where           = ("id",page_id)
                )[0]
            page_id  = result["parent"]
            data.append( result["name"] )

        # Liste umdrehen
        data.reverse()

        return "/" + "/".join(data)

    def get_sitemap_data( self ):
        """ Alle Daten die für`s Sitemap benötigt werden """
        return self.select(
                select_items    = [ "id","name","title","parent"],
                from_table      = "pages",
                where           = [ ("showlinks",1), ("permitViewPublic",1) ],
                order           = ("position","ASC"),
            )

    #_____________________________________________________________________________
    ## Funktionen für das ändern des Looks (Styles, Templates usw.)

    def get_style_list( self ):
        return self.select(
                select_items    = ["id","name","description"],
                from_table      = "styles",
            )

    def get_style_data( self, style_id ):
        return self.select(
                select_items    = ["name","description","content"],
                from_table      = "styles",
                where           = ("id", style_id)
            )[0]

    def update_style( self, style_id, style_data ):
        self.update(
            table   = "styles",
            data    = style_data,
            where   = ("id",style_id),
            limit   = 1
        )

    def get_template_list( self ):
        return self.select(
                select_items    = ["id","name","description"],
                from_table      = "templates",
            )

    def get_template_data( self, template_id ):
        return self.select(
                select_items    = ["name","description","content"],
                from_table      = "templates",
                where           = ("id", template_id)
            )[0]

    def update_template( self, template_id, template_data ):
        self.update(
            table   = "templates",
            data    = template_data,
            where   = ("id",template_id),
            limit   = 1
        )

    #_____________________________________________________________________________
    ## InterneSeiten

    def get_internal_page_list( self ):
        return self.select(
                select_items    = ["name","description","markup"],
                from_table      = "pages_internal",
            )

    def get_internal_page_data( self, internal_page_name ):
        return self.select(
                select_items    = ["markup","content","description"],
                from_table      = "pages_internal",
                where           = ("name", internal_page_name)
            )[0]

    def update_internal_page( self, internal_page_name, page_data ):
        self.update(
            table   = "pages_internal",
            data    = page_data,
            where   = ("name",internal_page_name),
            limit   = 1
        )

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

    #_____________________________________________________________________________
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







