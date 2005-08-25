#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Alles was mit dem ändern von Inhalten zu tun hat:
    -edit_page
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.0.7"

__history__="""
v0.0.7
    - "must_admin" für Module-Manager definiert
    - Nutzt Zeitumwandlung aus PyLucid["tools"]
v0.0.6
    - vereinfachung in parent_tree.make_parent_option() durch MySQLdb.cursors.DictCursor
v0.0.5
    - NEU: Pseudo Klasse 'module_info' liefert Daten für den Module-Manager
v0.0.4
    - NEU: erstellen einer Seite
v0.0.3
    - NEU: encoding from DB (Daten werden in einem bestimmten Encoding aus der DB geholt)
v0.0.2
    - Fehler behoben: parend-ID wird nach einem Preview auf 'root' gesetzt
v0.0.1
    - erste Version
"""

__todo__ = """
lastupdatetime in der SQL Datenbank ändern: time-String keine gute Idee: in lucidCMS wird
das Archiv nicht mehr angezeigt :(
"""

# Python-Basis Module einbinden
import sys, cgi, time, pickle

# Interne PyLucid-Module einbinden
import config



# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"






#_______________________________________________________________________
# Module-Manager Daten für den page_editor


class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "edit_page" : {
            "txt_menu"      : "edit page",
            "txt_long"      : "edit the current page",
            "section"       : "front menu",
            "must_login"    : True,
            "must_admin"    : False,
            "get_page_id"   : True,
        },
        "new_page" : {
            "txt_menu"      : "new page",
            "txt_long"      : "make a new page here",
            "section"       : "front menu",
            "must_login"    : True,
            "must_admin"    : True,
            "get_page_id"   : True,
        },
    }












#_______________________________________________________________________



class parent_tree:
    """
    Generiert eine Auswahlliste aller Seiten
    Wird beim editieren für die parent-Seiten-Auswahl benötigt
    """
    def __init__( self, db ):
        self.db = db

    def make_parent_option( self ):
        # Daten aus der DB holen
        SQLcommand  = "SELECT id, name, parent"#, position"
        SQLcommand += " FROM $tableprefix$pages"
        SQLcommand += " ORDER BY position ASC"

        data = self.db.get( SQLcommand )

        # Daten umformen
        tmp = {}
        for line in data:
            parent  = line["parent"]
            id_name = ( line["id"], line["name"] )
            if tmp.has_key( line["parent"] ):
                tmp[parent].append( id_name )
            else:
                tmp[parent] = [ id_name ]

        self.tree = [ (0, "_| root") ]
        self.build( tmp, tmp.keys() )
        return self.tree

    def build( self, tmp, keys, parent=0, deep=1 ):
        "Bildet aus den Aufbereiteten Daten"
        if not tmp.has_key( parent ):
            # Seite hat keine Unterseiten
            return deep-1

        for id, name in tmp[parent]:
            # Aktuelle Seite vermerken
            self.tree.append( (id, "%s| %s" % ("_"*(deep*3),name) ) )
            #~ print "_"*(deep*3) + name
            deep = self.build( tmp, keys, id, deep+1 )

        return deep-1

#~ if __name__ == "__main__":
    #~ testdaten = {
        #~ 0: [(1, "eins"), (13, "zwei"), (9, "drei")],
        #~ 13: [(14, "zwei 1"), (15, "zwei 2")],
        #~ 14: [(16, "zwei 2 drunter")]
    #~ }
    #~ pt = parent_tree("")
    #~ pt.tree = []
    #~ pt.build( testdaten, testdaten.keys() )
    #~ for id,name in pt.tree:
        #~ print "%2s - %s" % (id,name)
    #~ sys.exit()


#_______________________________________________________________________


class page_editor:
    """
    Editieren einer CMS-Seite mit Preview und Archivierung
    """
    def __init__( self, PyLucid ):
        self.PyLucid    = PyLucid

        self.config         = PyLucid["config"]
        #~ self.config.debug()
        self.CGIdata        = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.session        = PyLucid["session"]
        #~ self.session.debug()
        self.db             = PyLucid["db"]
        #~ self.auth       = PyLucid["auth"]
        self.page_msg       = PyLucid["page_msg"]
        self.preferences    = PyLucid["preferences"]
        self.tools          = PyLucid["tools"]

    def action( self ):
        #~ self.CGIdata.debug()
        if self.CGIdata.has_key( 'Submit' ):
            if self.CGIdata["Submit"] == "preview":
                self.session["last_action"] = "preview edit page"
                return self.preview_page()
            elif self.CGIdata["Submit"] == "save":
                self.session["last_action"] = "save edit page"
                return self.save_page()
            elif self.CGIdata["Submit"] == "encode from DB":
                return self.edit_page( encode_from_db=True )
            else:
                return "<h1>Error!</h1>Command: '%s' unknow! Please check internal page content!" % self.CGIdata["Submit"]
        elif self.CGIdata.has_key( 'command' ):
            if self.CGIdata["command"] == "edit_page":
                return self.edit_page()
            elif self.CGIdata["command"] == "new_page":
                return "<h3>make new page</h3>" + self.new_page()

        return "<h1>command error</h1>"

    def new_page( self ):
        "Neue Seite soll angelegt werden"

        if self.session["isadmin"] != 1:
            return "<h1>Error: You can't create a new Side. You not an admin.</h1>"

        core = self.preferences["core"]

        page_data = {
            "parent"            : int( self.CGIdata["page_id"] ),
            "name"              : "NewSide",
            "template"          : core["defaultTemplate"],
            "style"             : core["defaultStyle"],
            "markup"            : core["defaultMarkup"],
            "showlinks"         : core["defaultShowLinks"],
            "permitViewPublic"  : core["defaultPermitPublic"],
            "ownerID"           : self.session["user_id"],
            "permitViewGroupID" : 1,
            "permitEditGroupID" : 1,
            "title"             : "",
            "content"           : "",
            "keywords"          : "",
            "description"       : "",
        }

        # Damit man bei self.save() noch weiß, das es eine neue Seite ist ;)
        self.session["make_new_page"] = 1

        return self.editor_page( page_data )

    def get_page_data( self, page_id ):
        "Liefert alle Daten die zum editieren einer Seite notwendig sind zurück"
        return self.db.page_items_by_id(
                item_list   = ["parent", "name", "title", "template", "style",
                                "markup", "content", "keywords", "description",
                                "showlinks", "permitViewPublic", "permitViewGroupID",
                                "ownerID", "permitEditGroupID"],
                page_id     = page_id
            )

    def check_user_rights( self ):
        pass

    def edit_page( self, encode_from_db=False ):
        page_data = self.get_page_data( self.CGIdata["page_id"] )

        status_msg = "" # Nachricht für encodieren

        if encode_from_db:
            # Daten aus der DB sollen convertiert werden
            encoding = self.CGIdata["encoding"]

            try:
                page_data["content"] = page_data["content"].decode( encoding ).encode( "utf8" )
                status_msg = "<h3>[Encoded from DB with '%s']</h3>" % encoding
            except Exception, e:
                status_msg = "<h3>%s</h3>" % e

        return self.editor_page( page_data, status_msg )

    def editor_page( self, edit_page_data, status_msg="" ):
        #~ print "Content-type: text/html\n\n<pre>"
        #~ for k,v in edit_page_data.iteritems(): print k," - ",v," ",cgi.escape( str(type(v)) )
        #~ print "</pre>"
        #~ self.CGIdata.debug()

        internal_page = self.db.get_internal_page("edit_page")

        if str( edit_page_data["showlinks"] ) == "1":
            showlinks = " checked"
        else:
            showlinks = ""

        if str( edit_page_data["permitViewPublic"] ) == "1":
            permitViewPublic = " checked"
        else:
            permitViewPublic = ""

        if not edit_page_data.has_key( "summary" ):
            # Information kommt nicht von der Seite, ist aber beim Preview schon vorhanden!
            edit_page_data["summary"] = ""

        MyOptionMaker = self.tools.html_option_maker()

        encoding_option = MyOptionMaker.build_from_list( ["utf8","iso-8859-1"], "utf8" )
        markup_option   = MyOptionMaker.build_from_list( self.config.available_markups, edit_page_data["markup"] )

        parent_option = parent_tree( self.db ).make_parent_option()
        parent_option = MyOptionMaker.build_from_list( parent_option, int( edit_page_data["parent"] ) )


        def make_option( table_name, select_item ):
            """ Speziallfall: Select Items sind immer "id" und "name" """
            return MyOptionMaker.build_from_dict(
                data            = self.db.select( ("id","name"), table_name ),
                value_name      = "id",
                txt_name        = "name",
                select_item     = select_item
            )

        template_option             = make_option( "templates", edit_page_data["template"] )
        style_option                = make_option( "styles", edit_page_data["style"] )
        ownerID_option              = make_option( "users", edit_page_data["ownerID"] )
        permitEditGroupID_option    = make_option( "groups", edit_page_data["permitEditGroupID"] )
        permitViewGroupID_option    = make_option( "groups", edit_page_data["permitViewGroupID"] )

        if edit_page_data["content"] == None:
            # Wenn eine Seite mit lucidCMS frisch angelegt wurde und noch kein
            # Text eingegeben wurde, ist "content" == None -> Das Produziert
            # beim cgi.escape( edit_page_data["content"] ) einen traceback :(
            # und so nicht:
            edit_page_data["content"] = ""

        #~ edit_page_data["content"] += "\n\n" + str( edit_page_data )
        form_url = "%s?command=edit_page&page_id=%s" % ( self.config.system.real_self_url, self.CGIdata["page_id"] )

        try:
            content = ""
            if self.session["isadmin"] != 1:
                content += "<strong>You can not edit this page! You have no permissions!</strong>"

            content += internal_page["content"] % {
                        "status_msg"                : status_msg, # Nachricht beim encodieren
                        # Textfelder
                        "url"                       : form_url,
                        "summary"                   : edit_page_data["summary"],
                        "name"                      : edit_page_data["name"],
                        "title"                     : edit_page_data["title"],
                        "keywords"                  : edit_page_data["keywords"],
                        "description"               : edit_page_data["description"],
                        "content"                   : cgi.escape( edit_page_data["content"] ),
                        # Checkboxen
                        "showlinks"                 : showlinks,
                        "permitViewPublic"          : permitViewPublic,
                        # List-Optionen
                        "encoding_option"           : encoding_option,
                        "markup_option"             : markup_option,
                        "parent_option"             : parent_option,
                        "template_option"           : template_option,
                        "style_option"              : style_option,
                        "ownerID_option"            : ownerID_option,
                        "permitEditGroupID_option"  : permitEditGroupID_option,
                        "permitViewGroupID_option"  : permitViewGroupID_option,
                    }
        except KeyError, e:
            return "<h1>generate internal Page fail:</h1><h4>KeyError:'%s'</h4>" % e

        return content

    def set_default( self, dictionary ):
        """
        Kompletiert evtl. nicht vorhandene Keys.
        Leere HTML-input-Felder erscheinen nicht in den CGIdaten, diese müßen
        aber für die weiterverarbeitung im Dict als keys mit leeren (="") value
        erscheinen.
        """
        key_list = ("name", "title", "content", "keywords", "description", "showlinks", "permitViewPublic")
        for key in key_list:
            if not dictionary.has_key( key ):
                dictionary[key] = ""
        return dictionary

    #~ def encode_from_db( self ):
        #~ "Hohlt die Daten nochmals aus der "

    def preview_page( self ):
        "Preview einer editierten Seite"
        #~ self.CGIdata.debug()

        # CGI-Daten holen und leere Form-Felder "einfügen"
        edit_page_data = self.set_default( self.CGIdata )

        # CGI daten sind immer vom type str, die parent ID muß allerdings eine Zahl sein.
        # Ansonsten wird in MyOptionMaker.build_html_option() kein 'selected'-Eintrag gesetzt :(
        edit_page_data["parent"] = int( edit_page_data["parent"] )

        # Preview der Seite erstellen
        content = "\n<h3>edit preview:</h3>\n"
        content += '<div id="page_edit_preview">\n'
        from PyLucid_system import pagerender
        pagerender = pagerender.pagerender( self.PyLucid )
        content += pagerender.apply_markup( edit_page_data["content"], edit_page_data["markup"] )
        content += "\n</div>\n"

        # Formular der Seite zum ändern wieder dranhängen
        content += self.editor_page( edit_page_data )

        return content

    def save_page( self ):
        "Abspeichern einer editierten Seite"
        if self.session["isadmin"] != 1:
            return "<strong>You can not edit this page! You have no permissions!</strong>"

        # CGI-Daten holen und leere Form-Felder "einfügen"
        new_page_data = self.set_default( self.CGIdata )

        if not self.session.has_key("make_new_page"):
            # Nur beim editieren, wird evtl. die vorherige Seite Archiviert.
            # Das wird allerdings nicht beim erstellen einer neuen Seite gemacht ;)
            if self.CGIdata.has_key( "trivial" ):
                self.page_msg( "trivial modifications selected. Old side is not archived." )
            else:
                # Nur bei einer nicht trivialen Änderung, wird das Datum aktualisiert
                new_page_data["lastupdatetime"] = self.tools.convert_time_to_sql( time.time() )

                old_page_data = self.get_page_data( self.CGIdata["page_id"] )

                #~ for k,v in old_page_data.iteritems():
                    #~ content += "%s - %s<br>" % (k,v)
                #~ content += "<hr>"

                archiv_data = {
                    "userID"    : self.session["user_id"],
                    "type"      : "PyLucid,page",
                    "date"      : new_page_data["lastupdatetime"],
                    "content"   : pickle.dumps( old_page_data )
                }
                if self.CGIdata.has_key( "summary" ):
                    archiv_data["comment"] = self.CGIdata["summary"]

                self.db.insert( "archive", archiv_data )

                end_time = time.time()

                self.page_msg( "Archived old sidedata." )

        #~ for k,v in self.CGIdata.iteritems():
            #~ content += "%s - %s<br>" % (k,v)
        #~ content += "<hr>"
        #~ for k,v in self.session.iteritems():
            #~ content += "%s - %s<br>" % (k,v)
        #~ content += "<hr>"
        #~ content += str( self.id_of_edit_page )

        item_list   = ["parent", "name", "title", "parent", "template", "style",
                "markup", "content", "keywords", "description",
                "showlinks", "permitViewPublic", "permitViewGroupID",
                "ownerID", "permitEditGroupID"
            ]

        # CGI-Daten holen, die SeitenInformationen enthalten
        new_page_data = {}
        for item in item_list:
            if self.CGIdata.has_key( item ):
                new_page_data[item] = self.CGIdata[item]

        # Daten ergänzen
        new_page_data["lastupdateby"]   = self.session["user_id"]
        new_page_data["lastupdatetime"] = self.tools.convert_time_to_sql( time.time() ) # Letzte Änderungszeit

        if self.session.has_key("make_new_page"):
            # Eine neue Seite soll gespeichert werden
            new_page_data["datetime"] = new_page_data["lastupdatetime"] # Erstellungszeit
            new_page_data["position"] = 1
            try:
                self.db.insert(
                        table   = "pages",
                        data    = new_page_data,
                    )
                del( self.session["make_new_page"] )
            except Exception, e:
                return "<h3>Error to insert new side:'%s'</h3><p>Use browser back botton!</p>" % e

            self.page_msg( "New side saved." )
            return

        # Eine Seite wurde editiert.
        try:
            self.db.update(
                    table   = "pages",
                    data    = new_page_data,
                    where   = ("id",self.CGIdata["page_id"]),
                    limit   = 1
                )
        except Exception, e:
            return "<h3>Error to update side data: '%s'</h3>" % e

        self.page_msg( "New side data updated." )



#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid ):
    # Aktion starten
    return page_editor( PyLucid ).action()












