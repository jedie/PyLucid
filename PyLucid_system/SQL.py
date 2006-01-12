#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Anbindung an die SQL-Datenbank
"""

__version__="0.2.2"

__history__="""
v0.2.2
    - Umstellung bei Internen Seiten: Markup/Template
v0.2.1
    - Bessere Fehlerbehandlung beim Zugriff auf die Internen seiten.
v0.2
    - NEU: get_last_logs()
    - Bug in delete_style
v0.1
    - NEU: new_internal_page()
v0.0.11
    - Bug in get_internal_page() bei Fehlerabfrage.
v0.0.10
    - In get_side_data() wird bei keywords und description beim Wert None automatisch ein ="" gemacht
v0.0.9
    - NEU: print_internal_page() Sollte ab jetzt immer direkt genutzt werden, wenn eine interne Seite
        zum einsatzt kommt. Damit zentral String-Operating Fehler abgefangen werden.
v0.0.8
    - Nun können auch page_msg abgesetzt werden. Somit kann man hier mehr Inteligenz bei Fehlern einbauen
    - Neue Fehlerausgabe bei get_internal_page() besser im zusammenhang mit dem Modul-Manager
    - Neu: userdata()
    - Neu: get_available_markups()
v0.0.7
    - order=("name","ASC") bei internal_page-, style- und template-Liste eingefügt
    - get_page_link_by_id() funktioniert auch mit Sonderzeichen im Link
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

import urllib, pickle, sys, time

# Interne PyLucid-Module einbinden
from mySQL import mySQL
from config import dbconf




class db( mySQL ):
    """
    Erweitert den allgemeinen SQL-Wrapper (mySQL.py) um
    spezielle PyLucid-Funktionen.
    """
    def __init__( self, PyLucid ):
        #~ print "Content-type: text/html\n"
        #~ print "<h2>Connecte zur DB!</h2>"
        #~ import inspect
        #~ for line in inspect.stack(): print line,"<br>"

        #~ try:
            # SQL connection aufbauen
        mySQL.__init__( self, PyLucid )
                #~ unicode = 'utf-8'
                #~ use_unicode = True
            #~ )
        #~ except Exception, e:
            #~ print "Content-type: text/html\n"
            #~ print "<h1>PyLucid - Error</h1>"
            #~ print "<h2>Can't connect to SQL-DB: '%s'</h2>" % e
            #~ import sys
            #~ sys.exit()

        self.page_msg   = PyLucid["page_msg"]
        self.CGIdata    = PyLucid["CGIdata"]
        self.tools      = PyLucid["tools"]

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

        if side_data["keywords"] == None:
            side_data["keywords"] = ""

        if side_data["description"] == None:
            side_data["description"] = ""

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
                "Can't get Template: %s" % e,
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
        if not result:
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
        liefert die parend ID anhand des Namens zurück
        """
        # Anhand des Seitennamens wird die aktuelle SeitenID und den ParentID ermittelt
        return self.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("name",page_name)
            )[0]["parent"]

    def parentID_by_id( self, page_id ):
        """
        Die parent ID zur >page_id<
        """
        return self.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("id",page_id)
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

        data = self.db.None_convert(data, ("content",), "")

        return data

    def page_items_by_id( self, item_list, page_id ):
        "Allgemein: Daten zu einer Seite"
        page_items = self.select(
                select_items    = item_list,
                from_table      = "pages",
                where           = ("id", page_id)
            )[0]
        for i in ("name", "title", "content", "keywords", "description"):
            if page_items.has_key(i) and page_items[i]==None:
                page_items[i]=""
        return page_items

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

        data = [urllib.quote_plus(i) for i in data]

        return "/" + "/".join(data)

    def get_sitemap_data( self ):
        """ Alle Daten die für`s Sitemap benötigt werden """
        return self.select(
                select_items    = ["id","name","title","parent"],
                from_table      = "pages",
                where           = [("showlinks",1), ("permitViewPublic",1)],
                order           = ("position","ASC"),
            )

    def get_sequencing_data(self):
        """ Alle Daten die für pageadmin.sequencing() benötigt werden """
        parend_id = self.parentID_by_id(self.CGIdata["page_id"])
        return self.select(
                select_items    = ["id","name","title","parent","position"],
                from_table      = "pages",
                where           = ("parent", parend_id),
                order           = ("position","ASC"),
            )

    #_____________________________________________________________________________
    ## Funktionen für das ändern des Looks (Styles, Templates usw.)

    def get_style_list( self ):
        return self.select(
                select_items    = ["id","name","description"],
                from_table      = "styles",
                order           = ("name","ASC"),
            )

    def get_style_data( self, style_id ):
        return self.select(
                select_items    = ["name","description","content"],
                from_table      = "styles",
                where           = ("id", style_id)
            )[0]

    def get_style_data_by_name( self, style_name ):
        return self.select(
                select_items    = ["description","content"],
                from_table      = "styles",
                where           = ("name", style_name)
            )[0]

    def update_style( self, style_id, style_data ):
        self.update(
            table   = "styles",
            data    = style_data,
            where   = ("id",style_id),
            limit   = 1
        )

    def new_style( self, style_data ):
        self.insert(
            table   = "styles",
            data    = {
                "name"          : style_data["name"],
                "plugin_id"     : style_data.get("plugin_id", None),
                "description"   : style_data.get("description", None),
                "content"       : style_data["content"],
            },
        )

    def delete_style(self, style):
        if type(style) == str:
            # Der style-Name wurde angegeben
            style_id = self.select(
                select_items    = ["id"],
                from_table      = "styles",
                where           = ("name", style)
            )[0]["id"]
        else:
            style_id = style

        self.delete(
            table   = "styles",
            where   = ("id",style_id),
            limit   = 1
        )

    def delete_style_by_plugin_id(self, plugin_id):
        style_names = self.select(
            select_items    = ["name"],
            from_table      = "styles",
            where           = ("plugin_id",plugin_id),
        )
        self.delete(
            table   = "styles",
            where   = ("plugin_id",plugin_id),
            limit   = 99,
        )
        style_names = [i["name"] for i in style_names]
        return style_names

    def get_template_list( self ):
        return self.select(
                select_items    = ["id","name","description"],
                from_table      = "templates",
                order           = ("name","ASC"),
            )

    def get_template_data( self, template_id ):
        return self.select(
                select_items    = ["name","description","content"],
                from_table      = "templates",
                where           = ("id", template_id)
            )[0]

    def get_template_data_by_name( self, template_name ):
        return self.select(
                select_items    = ["description","content"],
                from_table      = "templates",
                where           = ("name", template_name)
            )[0]

    def update_template( self, template_id, template_data ):
        self.update(
            table   = "templates",
            data    = template_data,
            where   = ("id",template_id),
            limit   = 1
        )

    def new_template( self, template_data ):
        self.insert(
            table   = "templates",
            data    = template_data,
        )

    def delete_template( self, template_id ):
        self.delete(
            table   = "templates",
            where   = ("id",template_id),
            limit   = 1
        )

    def change_page_position( self, page_id, position ):
        self.update(
            table   = "pages",
            data    = {"position":position},
            where   = ("id",page_id),
            limit   = 1
        )

    #_____________________________________________________________________________
    ## InterneSeiten

    def get_internal_page_list( self ):
        return self.select(
                select_items    = [
                    "name","plugin_id","description",
                    "markup","template_engine","markup"
                ],
                from_table      = "pages_internal",
            )

    def get_internal_page_dict(self):
        page_dict = {}
        for page in self.get_internal_page_list():
            page_dict[page["name"]] = page
        return page_dict

    def get_internal_category( self ):
        return self.select(
                select_items    = ["id","module_name"],
                from_table      = "plugins",
                order           = ("module_name","ASC"),
            )

    def get_template_engine(self, id):
        """ Liefert den template_engine-Namen anhand der ID """
        if id==None:
            # Existiert auch als ID
            id = "None"

        try:
            return self.select(
                select_items    = ["name"],
                from_table      = "template_engines",
                where           = ("id", id)
            )[0]["name"]
        except IndexError:
            self.page_msg("Can't get template engine name for id '%s'. " % id)
            return "none"

    def get_template_engine_id(self, name):
        if type(name)==int:
            # Ist wohl schon die ID-Zahl
            return name

        if name==None:
            # None existiert auch als ID
            name="None"
        else:
            name = name.replace("_", " ")

        try:
            return self.select(
                select_items    = ["id"],
                from_table      = "template_engines",
                where           = ("name", name)
            )[0]["id"]
        except IndexError:
            self.page_msg("Warning: Can't get ID for template engine namend '%s'" % name)
            return None

    def get_internal_page_data(self, internal_page_name, replace=True):
        try:
            data = self.select(
                select_items    = ["template_engine","markup","content","description"],
                from_table      = "pages_internal",
                where           = ("name", internal_page_name)
            )[0]
        except Exception, e:
            import inspect
            raise KeyError(
                "Internal page '%s' not found (from '...%s' line %s): %s" % (
                    internal_page_name, inspect.stack()[1][1][-20:], inspect.stack()[1][2], e
                )
            )

        if replace==True:
            data["template_engine"] = self.get_template_engine(data["template_engine"])
            data["markup"] = self.get_markup_id(data["markup"])

        return data


    def print_internal_page(self, internal_page_name, page_dict={}):
        """
        Interne Seite aufgeüllt mit Daten ausgeben. Diese Methode sollte immer
        verwendet werden, weil sie eine gescheite Fehlermeldung anzeigt.

        Wird für template-engine = "None" und = "string formatting" verwendet.
        """

        try:
            internal_page_data = self.get_internal_page_data(internal_page_name)
        except Exception, e:
            import inspect
            print "[Can't print internal page '%s' (from '...%s' line %s): %s]" % (
                internal_page_name, inspect.stack()[1][1][-20:], inspect.stack()[1][2], e
            )
            return

        # Wenn kein oder ein leeres Dict angegeben wurde, kann es keine "string formatting" Seite sein.
        if page_dict=={}:
            template_engine = "None"
        else:
            template_engine = "string formatting"

        if internal_page_data["template_engine"] != template_engine:
            self.page_msg(
                "Warning: Internal page '%s' is not marked as a '%s' page! "
                "(Marked as:'%s')" % (
                    internal_page_name, template_engine, internal_page_data["template_engine"]
                )
            )

        content = internal_page_data["content"]

        try:
            print content % page_dict
        except Exception, e:
            self.page_msg("Error information:")

            s = self.tools.Find_StringOperators(content)
            if s.incorrect_hit_pos != []:
                self.page_msg(" -"*40)
                self.page_msg("There are incorrect %-chars in the internal_page:")
                self.page_msg("Text summary:")
                for line in s.get_incorrect_text_summeries():
                    self.page_msg(line)
                self.page_msg(" -"*40)

            l = s.correct_tags
            # doppelte Einträge löschen (auch mit Python >2.3)
            content_placeholder = [l[i] for i in xrange(len(l)) if l[i] not in l[:i]]
            content_placeholder.sort()
            self.page_msg("*** %s content placeholder:" % len(content_placeholder))
            self.page_msg(content_placeholder)

            l = page_dict.keys()
            given_placeholder = [l[i] for i in xrange(len(l)) if l[i] not in l[:i]]
            given_placeholder.sort()
            self.page_msg("*** %s given placeholder:" % len(given_placeholder))
            self.page_msg(given_placeholder)

            diff_placeholders = []
            for i in content_placeholder:
                if (not i in given_placeholder) and (not i in diff_placeholders):
                    diff_placeholders.append(i)
            for i in given_placeholder:
                if (not i in content_placeholder) and (not i in diff_placeholders):
                    diff_placeholders.append(i)

            diff_placeholders.sort()
            self.page_msg("*** placeholder diffs:", diff_placeholders)

            raise Exception(
                "%s: '%s': Can't fill internal page '%s'. \
                *** More information above in page message ***" % (
                    sys.exc_info()[0], e, internal_page_name,
                )
            )

    def get_internal_page(self, internal_page_name, page_dict={}):
        """
        Interne Seite aufgeüllt mit Daten ausgeben. Diese Methode sollte immer
        verwendet werden, weil sie eine gescheite Fehlermeldung anzeigt.
        """
        internal_page = self.get_internal_page_data(internal_page_name)

        try:
            internal_page["content"] = internal_page["content"] % page_dict
        except KeyError, e:
            import re
            placeholder = re.findall(r"%\((.*?)\)s", internal_page["content"])
            raise KeyError(
                "KeyError %s: Can't fill internal page '%s'. \
                placeholder in internal page: %s given placeholder for that page: %s" % (
                    e, internal_page_name, placeholder, page_dict.keys()
                )
            )
        return internal_page

    def print_internal_TAL_page(self, internal_page_name, context_dict):

        internal_page_data = self.get_internal_page_data(internal_page_name)
        internal_page_content = internal_page_data["content"]
        if internal_page_data["template_engine"] != "TAL":
            self.page_msg(
                "Warning: Internal page '%s' is not marked as a TAL page! "
                "(Marked as:'%s')" % (
                    internal_page_name, internal_page_data["template_engine"]
                )
            )

        if internal_page_data["markup"] != None:
            self.page_msg(
                "Warning: A TAL page should never have markup! "
                "(internal page name: '%s', Markup:'%s')" % (
                    internal_page_name, internal_page_data["markup"]
                )
            )

        from PyLucid_simpleTAL import simpleTAL, simpleTALES

        context = simpleTALES.Context(allowPythonPath=1)
        context.globals.update(context_dict) # context.addGlobal()

        template = simpleTAL.compileHTMLTemplate(internal_page_content, inputEncoding="UTF-8")
        template.expand(context, sys.stdout, outputEncoding="UTF-8")

    def update_internal_page( self, internal_page_name, page_data ):
        self.update(
            table   = "pages_internal",
            data    = page_data,
            where   = ("name",internal_page_name),
            limit   = 1
        )

    #~ def get_internal_group_id( self ):
        #~ """
        #~ Liefert die ID der internen PyLucid Gruppe zurück
        #~ Wird verwendet für interne Seiten!
        #~ """
        #~ internal_group_name = "PyLucid_internal"
        #~ return self.select(
                #~ select_items    = ["id"],
                #~ from_table      = "groups",
                #~ where           = ("name", internal_group_name)
            #~ )[0]["id"]

    def get_internal_page_category_id(self, category_name):
        """
        Liefert die ID anhand des Kategorie-Namens zurück
        Existiert die Kategorie nicht, wird sie in die Tabelle eingefügt.
        """
        try:
            return self.select(
                select_items    = ["id"],
                from_table      = "pages_internal_category",
                where           = ("name", category_name)
            )[0]["id"]
        except IndexError:
            # Kategorier existiert noch nicht -> wird erstellt
            self.insert(
                table = "pages_internal_category",
                data  = {"name": category_name}
            )
            return self.cursor.lastrowid

    def delete_blank_pages_internal_categories(self):
        """
        Löscht automatisch überflüssige Kategorieren.
        d.h. wenn es keine interne Seite mehr gibt, die in
        der Kategorie vorkommt, wird sie gelöscht
        """
        used_categories = self.select(
            select_items    = ["category_id"],
            from_table      = "pages_internal",
        )
        used_categories = [i["category_id"] for i in used_categories]

        existing_categories = self.select(
            select_items    = ["id","name"],
            from_table      = "pages_internal_category",
        )

        deleted_categories = []
        for line in existing_categories:
            if not line["id"] in used_categories:
                self.delete(
                    table = "pages_internal_category",
                    where = ("id", line["id"]),
                    limit = 99,
                )
                deleted_categories.append(line["name"])
        return deleted_categories

    def new_internal_page(self, data, lastupdatetime=None):
        """
        Erstellt eine neue interne Seite.
        """

        markup_id = self.get_markup_id(data["markup"])
        category_id = self.get_internal_page_category_id(data["category"])
        template_engine_id = self.get_template_engine_id(data["template_engine"])
        #~ print "category_id:", category_id

        self.insert(
            table = "pages_internal",
            data  = {
                "name"              : data["name"],
                "plugin_id"         : data["plugin_id"],
                "category_id"       : category_id,
                "template_engine"   : template_engine_id,
                "markup"            : markup_id,
                "lastupdatetime"    : self.tools.convert_time_to_sql(lastupdatetime),
                "content"           : data["content"],
                "description"       : data["description"],
            },
        )

    def delete_internal_page(self, name):
        self.delete(
            table = "pages_internal",
            where = ("name", name),
            limit = 1,
        )
        #~ self.delete_blank_pages_internal_categories()

    def delete_internal_page_by_plugin_id(self, plugin_id):
        #~ print "plugin_id:", plugin_id
        page_names = self.select(
            select_items    = ["name"],
            from_table      = "pages_internal",
            where           = ("plugin_id", plugin_id),
        )
        #~ print "page_names:", page_names
        self.delete(
            table = "pages_internal",
            where = ("plugin_id", plugin_id),
            limit = 99,
        )
        page_names = [i["name"] for i in page_names]
        return page_names

    #_____________________________________________________________________________
    ## Userverwaltung

    def normal_login_userdata( self, username ):
        "Userdaten die bei einem normalen Login benötigt werden"
        return self.select(
                select_items    = ["id", "password", "admin"],
                from_table      = "md5users",
                where           = ("name", username)
            )[0]

    def userdata( self, username ):
        return self.select(
                select_items    = ["id", "name","realname","email","admin"],
                from_table      = "md5users",
                where           = ("name", username)
            )[0]

    def add_md5_User( self, name, realname, email, pass1, pass2, admin ):
        "Hinzufügen der Userdaten in die PyLucid's JD-md5-user-Tabelle"
        self.insert(
                table = "md5users",
                data  = {
                    "name"      : name,
                    "realname"  : realname,
                    "email"     : email,
                    "pass1"     : pass1,
                    "pass2"     : pass2,
                    "admin"     : admin
                }
            )

    def md5_login_userdata( self, username ):
        "Userdaten die beim JS-md5 Login benötigt werden"
        return self.select(
                select_items    = ["id", "pass1", "pass2", "admin"],
                from_table      = "md5users",
                where           = ("name", username)
            )[0]

    def exists_admin(self):
        """
        Existiert schon ein Admin?
        """
        result = self.select(
            select_items    = ["id"],
            from_table      = "md5users",
            limit           = (1,1)
        )
        if result:
            return True
        else:
            return False

    def user_table_data(self):
        """ wird in userhandling verwendet """
        return self.select(
            select_items    = ["id","name","realname","email","admin"],
            from_table      = "md5users",
        )

    def update_userdata(self, id, user_data):
        """ Editierte Userdaten wieder speichern """
        self.update(
            table   = "md5users",
            data    = user_data,
            where   = ("id",id),
            limit   = 1
        )

    def del_user(self, id):
        """ Löschen eines Users """
        self.delete(
            table   = "md5users",
            where   = ("id", id),
            limit   = 1
        )

    def user_info_by_id(self, id):
        return self.select(
            select_items    = ["id","name","realname","email","admin"],
            from_table      = "md5users",
            where           = ("id", id)
        )[0]

    #_____________________________________________________________________________
    ## Module / Plugins

    def activate_module(self, id):
        self.update(
            table   = "plugins",
            data    = {"active": 1},
            where   = ("id",id),
            limit   = 1
        )

    def deactivate_module(self, id):
        self.update(
            table   = "plugins",
            data    = {"active": 0},
            where   = ("id",id),
            limit   = 1
        )

    def get_active_module_data(self):
        """
        Module-Daten für den Modulemanager holen
        """
        select_items = ["id", "package_name", "module_name", "debug"]
        # Build-In Module holen
        data = self.select( select_items,
            from_table      = "plugins",
            where           = [("active", -1)],
        )
        # Sonstigen aktiven Module
        data += self.select( select_items,
            from_table      = "plugins",
            where           = [("active", 1)],
        )

        # Umformen zu einem dict mit dem Namen als Key
        result = {}
        for line in data:
            result[line['module_name']] = line

        return result

    def get_method_properties(self, plugin_id, method_name):

        def unpickle(SQL_result_list):
            for line in SQL_result_list:
                for item in ("CGI_laws", "get_CGI_data"):
                    if line[item] == None:
                        continue
                    #~ try:
                    line[item] = pickle.loads(line[item])
                    #~ except:
            return SQL_result_list


        data_items = [
            "must_login", "must_admin", "CGI_laws", "get_CGI_data", "menu_section",
            "menu_description","direct_out", "sys_exit", "has_Tags", "no_rights_error"
        ]
        # Daten der Methode holen
        method_properties = self.select(
            select_items    = ["id", "parent_method_id"] + data_items,
            from_table      = "plugindata",
            where           = [("plugin_id", plugin_id), ("method_name",method_name)],
        )
        method_properties = unpickle(method_properties)[0]

        # CGI_dependent_actions daten holen
        CGI_dependent_data = self.select(
            select_items    = ["method_name"] + data_items,
            from_table      = "plugindata",
            where           = ("parent_method_id", method_properties["id"]),
        )
        #~ self.page_msg(CGI_dependent_data, plugin_id, method_name)
        CGI_dependent_data = unpickle(CGI_dependent_data)

        return method_properties, CGI_dependent_data

    def install_plugin(self, module_data):
        """
        Installiert ein neues Plugin/Modul.
        Wichtig: Es wird extra jeder Wert herraus gepickt, weil in module_data
            mehr Keys sind, als in diese Tabelle gehören!!!
        """
        if module_data.has_key("essential_buildin") and module_data["essential_buildin"] == True:
            active = -1
        else:
            active = 0

        self.insert(
            table = "plugins",
            data  = {
                "package_name"              : module_data["package_name"],
                "module_name"               : module_data["module_name"],
                "version"                   : module_data["version"],
                "author"                    : module_data["author"],
                "url"                       : module_data["url"],
                "description"               : module_data["description"],
                "long_description"          : module_data["long_description"],
                "active"                    : active,
                "debug"                     : module_data["module_manager_debug"],
                "SQL_deinstall_commands"    : module_data["SQL_deinstall_commands"],
            }
        )
        return self.cursor.lastrowid

    def register_plugin_method(self, plugin_id, method_name, method_cfg, parent_method_id=None):

        where= [("plugin_id", plugin_id), ("method_name", method_name)]

        if parent_method_id != None:
            where.append(("parent_method_id", parent_method_id))

        if self.select(["id"], "plugindata", where):
            raise IntegrityError(
                "Duplicate entry '%s' with ID %s!" % (method_name, plugin_id)
            )

        # True und False in 1 und 0 wandeln
        for k,v in method_cfg.iteritems():
            if v == True:
                method_cfg[k] = 1
            elif v == False:
                method_cfg[k] = 0
            elif type(v) in (dict, list, tuple):
                method_cfg[k] = pickle.dumps(v)

        # Daten vervollständigen
        method_cfg.update({
            "plugin_id"     : plugin_id,
            "method_name"   : method_name,
        })

        if parent_method_id != None:
            method_cfg["parent_method_id"] = parent_method_id

        self.insert(
            table = "plugindata",
            data  = method_cfg
        )

    def get_method_id(self, plugin_id, method_name):
        """ Wird beim installieren eines Plugins benötigt """
        return self.select(
            select_items    = ["id"],
            from_table      = "plugindata",
            where           = [("plugin_id", plugin_id), ("method_name", method_name)],
        )[0]["id"]

    def get_plugin_id(self, package, module):
        """ Wird beim installieren eines Plugins benötigt """
        return self.select(
            select_items    = ["id"],
            from_table      = "plugins",
            where           = [("package_name", package), ("module_name", module)],
        )[0]["id"]

    def get_plugin_info_by_id(self, plugin_id):
        result = self.select(
            select_items    = ["package_name", "module_name"],
            from_table      = "plugins",
            where           = ("id", plugin_id),
        )[0]
        return result["package_name"], result["module_name"]

    def get_installed_modules_info(self):
        return self.select(
            select_items    = [
                "module_name", "package_name", "id","version","author","url","description","active"
            ],
            from_table      = "plugins",
        )

    def get_module_deinstall_info(self, id):
        deinstall_info = self.select(
            select_items    = [
                "module_name", "package_name", "SQL_deinstall_commands"
            ],
            from_table      = "plugins",
            where           = ("id", id),
        )[0]
        if deinstall_info["SQL_deinstall_commands"] != None:
            deinstall_info["SQL_deinstall_commands"] = pickle.loads(
                deinstall_info["SQL_deinstall_commands"]
            )

        return deinstall_info

    def delete_plugin(self, id):
        self.delete(
            table = "plugins",
            where = ("id", id),
            limit = 999,
        )

    def delete_plugindata(self, plugin_id):
        self.delete(
            table = "plugindata",
            where = ("plugin_id", plugin_id),
            limit = 999,
        )

    def get_plugindata(self, plugin_id):
        """
        Liefert plugindata Daten zurück.
        """
        return self.select(
            select_items    = ["*"],
            from_table      = "plugindata",
            where           = [("plugin_id", plugin_id)],
            #~ order           = ("parent_method_id","ASC"),
        )

    def get_plugin_menu_data(self, plugin_id):
        return self.select(
            select_items    = ["parent_method_id", "method_name", "menu_section", "menu_description"],
            from_table      = "plugindata",
            where           = [("plugin_id", plugin_id)]#,("parent_method_id", None)],
        )

    def get_internal_pages_info_by_module(self, plugin_id):
        """
        Informationen zu allen internen-Seiten von einem Plugin.
        Dabei werden die IDs von markup und lastupdateby direkt aufgelöst
        """
        pages_info = self.select(
            select_items    = [
                "name", "template_engine", "markup",
                "lastupdatetime", "lastupdateby", "description"
            ],
            from_table      = "pages_internal",
            where           = [("plugin_id", plugin_id)]
        )
        for page_info in pages_info:
            page_info["markup"] = self.get_markup_name(page_info["markup"])
            try:
                page_info["lastupdateby"] = self.user_info_by_id(page_info["lastupdateby"])["name"]
            except IndexError:
                pass
        return pages_info

    #_____________________________________________________________________________
    ## LOG

    def get_last_logs(self, limit=10):
        return self.select(
            select_items    = ["timestamp", "sid", "user_name", "domain", "message","typ","status"],
            from_table      = "log",
            order           = ("timestamp","DESC"),
            limit           = (0,limit)
        )

    #_____________________________________________________________________________
    ## Rechteverwaltung

    def get_permitViewPublic( self, page_id ):
        return self.select(
                select_items    = [ "permitViewPublic" ],
                from_table      = "pages",
                where           = ("id", page_id),
            )[0]["permitViewPublic"]

    #_____________________________________________________________________________
    ## Markup

    def get_markup_name(self, id_or_name):
        """
        Liefert von der ID den Markup Namen. Ist die ID schon der Name, ist
        das auch nicht schlimm.
        """
        try:
            markup_id = int(id_or_name)
        except:
            # Die Angabe ist offensichtlich schon der Name des Markups
            return id_or_name
        else:
            # Die Markup-ID Auflösen zum richtigen Namen
            return self.get_markupname_by_id( markup_id )

    def get_markup_id(self, id_or_name):
        """
        Liefert vom Namen des Markups die ID, auch dann wenn es schon die
        ID ist
        """
        if id_or_name == None:
            # Kein Markup wird einfach als None gehandelt
            return None

        try:
            return int(id_or_name) # Ist eine Zahl -> ist also schon die ID
        except:
            pass

        try:
            return self.select(
                select_items    = ["id"],
                from_table      = "markups",
                where           = ("name",id_or_name)
            )[0]["id"]
        except IndexError, e:
            raise IndexError("Can't get markup-ID for the name '%s' type: %s error: %s" % (
                    id_or_name, type(id_or_name), e
                )
            )

    def get_markupname_by_id(self, markup_id):
        """ Markup-Name anhand der ID """
        try:
            return self.select(
                select_items    = ["name"],
                from_table      = "markups",
                where           = ("id",markup_id)
            )[0]["name"]
        except IndexError:
            self.page_msg("Can't get markupname from markup id '%s' please edit this page and change markup!" % markup_id)
            return "none"

    def get_available_markups(self):
        """
        Bildet eine Liste aller verfügbaren Markups. Jeder Listeneintrag ist wieder
        eine Liste aus [ID,name]. Das ist ideal für tools.html_option_maker().build_from_list()
        """
        markups = self.select(
            select_items    = ["id","name"],
            from_table      = "markups",
        )
        result = []
        for markup in markups:
            result.append([markup["id"], markup["name"]])

        return result

    def get_available_template_engines(self):
        """
        Bildet eine Liste aller verfügbaren template_engines. Jeder Listeneintrag ist wieder
        eine Liste aus [ID,name]. Das ist ideal für tools.html_option_maker().build_from_list()
        """
        markups = self.select(
            select_items    = ["id","name"],
            from_table      = "template_engines",
        )
        result = []
        for markup in markups:
            result.append([markup["id"], markup["name"]])

        return result



class IntegrityError(Exception):
    pass