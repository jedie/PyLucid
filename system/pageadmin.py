#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Alles was mit dem �ndern von Inhalten zu tun hat:
    -edit_page
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.0.3"

__history__="""
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


#~ print "Content-type: text/html\n"


class option_maker:
    """
    Generiert eine HTML <option> 'Liste'
    z.B.:
        testdaten = ( (1,"eins"), (2,"zwei"), (3,"drei") )
        selected = 2
        print option_maker("").build_html_option( testdaten, selected ).replace("</option>","</option>\n")
    ergibt:
        <option value="1">eins</option>
        <option value="2" selected="selected">zwei</option>
        <option value="3">drei</option>
    """
    def __init__( self, db ):
        self.db = db

    def make( self, items, table, selected_item="", order_item="" ):
        data = self.get_data( items, table, order_item )
        #~ data = ((1L, 'managePages'), (2L, 'manageStyles'), (3L, 'manageTemplates'), (5L, 'PyLucid_internal'))
        #~ raise data
        return self.build_html_option( data, selected_item )

    def get_data( self, items, table, order_item ):
        # Daten aus der DB holen
        SQLcommand  = "SELECT %s" % ",".join(items)
        SQLcommand += " FROM $tableprefix$" + table
        if order_item != "":
            SQLcommand += " ORDER BY `id` ASC"
        return self.db.get( SQLcommand )


    def build_html_option( self, data, selected_item="" ):
        "Generiert aus >data< html-option-zeilen"
        try:
            test1,test2 = data[0]
        except ValueError:
            # data hat kein Wertepaar, also wird eins erzeugt ;)
            data = [(i,i) for i in data]

        result = ""
        for item1,item2 in data:
            if item1 == selected_item:
                selected = ' selected="selected"'
            else:
                selected = ""
            result += "\n" + str(item1) +"|"+ str(selected_item) + "\n"
            result += "\n" + str(type(item1)) +"|"+ str(type(selected_item)) + "\n"
            result += '<option value="%s"%s>%s</option>' % (item1,selected,item2)

        return result


#~ if __name__ == "__main__":
    #~ testdaten = (
        #~ ( 1, "___| eins"),
        #~ (13, "___| zwei"),
        #~ (14, "______| zwei 1"),
        #~ (16, "_________| zwei 2 drunter"),
        #~ (15, "______| zwei 2"),
        #~ ( 9, "___| drei")
    #~ )
    #~ print option_maker("").build_html_option( testdaten, 16 ).replace("</option>","</option>\n")
    #~ print "-"*80
    #~ testdaten = ["eins","zwei","drei"]
    #~ selected = "eins"
    #~ print option_maker("").build_html_option( testdaten, selected ).replace("</option>","</option>\n")
    #~ ## Soll ergeben:
    #~ # <option value="eins" selected="selected">eins</option>
    #~ # <option value="zwei">zwei</option>
    #~ # <option value="drei">drei</option>
    #~ sys.exit()



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
        SQLcommand += " FROM `lucid_pages`"
        SQLcommand += " ORDER BY `position` ASC"
        self.db.cursor.execute( SQLcommand )
        data = self.db.cursor.fetchall()

        # Daten umformen
        tmp = {}
        for item in data:
            id      = item[0]
            name    = item[1]
            parent  = item[2]
            if tmp.has_key( parent ):
                tmp[parent].append( (id,name) )
            else:
                tmp[parent] = [ (id,name) ]

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



class page_editor:
    """
    Editieren einer CMS-Seite mit Preview und Archivierung
    """
    def __init__( self, CGIdata, session, db, auth ):
        self.CGIdata    = CGIdata
        self.session    = session
        self.db         = db
        self.auth       = auth

    def get( self ):
        #~ self.CGIdata.debug()
        if self.CGIdata.has_key( 'Submit' ):
            if self.CGIdata["Submit"] == "preview":
                return self.preview_page()
            elif self.CGIdata["Submit"] == "save":
                return self.save_page()
            elif self.CGIdata["Submit"] == "encode from DB":
                return self.edit_page( encode_from_db=True )
            else:
                return "<h1>Error!</h1>Command: '%s' unknow! Please check internal page content!" % self.CGIdata["Submit"]

        return self.edit_page()


    def get_page_data( self, page_id ):
        "Liefert alle Daten die zum editieren einer Seite notwendig sind zurück"
        return self.db.page_items_by_id(
                item_list   = ["parent", "name", "title", "parent", "template", "style",
                                "markup", "content", "keywords", "description",
                                "showlinks", "permitViewPublic", "permitViewGroupID",
                                "ownerID", "permitEditGroupID"],
                page_id     = page_id
            )

    def check_user_rights( self ):
        pass

    def edit_page( self, encode_from_db=False ):
        id_of_edit_page = self.session["page_history"][0]
        self.session["edit_page_id"] = id_of_edit_page

        page_data = self.get_page_data(id_of_edit_page)

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
        #~ return "<br>".join( edit_page_data.keys() ) + "<hr>"
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

        MyOptionMaker = option_maker( self.db )

        encoding_option = ["utf8","iso-8859-1"]
        encoding_option = MyOptionMaker.build_html_option( encoding_option, "utf8" )

        markup_option = ["none","textile"]
        markup_option = MyOptionMaker.build_html_option( markup_option, edit_page_data["markup"] )

        parent_option = parent_tree( self.db ).make_parent_option()
        parent_option = MyOptionMaker.build_html_option( parent_option, edit_page_data["parent"] )

        template_option = MyOptionMaker.make(
                items=("id","name"), table="templates",
                selected_item=edit_page_data["template"],
                order_item="id"
            )
        style_option = MyOptionMaker.make(
                items=("id","name"), table="styles",
                selected_item=edit_page_data["style"],
                order_item="id"
            )
        ownerID_option = MyOptionMaker.make(
                items=("id","name"), table="users",
                selected_item=edit_page_data["ownerID"],
                order_item="id"
            )
        permitEditGroupID_option = MyOptionMaker.make(
                items=("id","name"), table="groups",
                selected_item=edit_page_data["permitEditGroupID"],
                order_item="id"
            )
        permitViewGroupID_option = MyOptionMaker.make(
                items=("id","name"), table="groups",
                selected_item=edit_page_data["permitViewGroupID"],
                order_item="id"
            )

        if edit_page_data["content"] == None:
            # Wenn eine Seite mit lucidCMS frisch angelegt wurde und noch kein
            # Text eingegeben wurde, ist "content" == None -> Das Produziert
            # beim cgi.escape( edit_page_data["content"] ) einen traceback :(
            # und so nicht:
            edit_page_data["content"] = ""

        #~ edit_page_data["content"] += "\n\n" + str( edit_page_data )

        try:
            content = ""
            if self.session["isadmin"] != 1:
                content += "<strong>You can not edit this page! You have no permissions!</strong>"

            content += internal_page["content"] % {
                        "status_msg"                : status_msg, # Nachricht beim encodieren
                        # Textfelder
                        "url"                       : config.system.real_self_url + "?command=edit_page",
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
        key_list = ("name", "title", "content", "keywords", "description")
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
        import pagerender
        pagerender = pagerender.pagerender( self.session, edit_page_data, self.db, self.auth )
        content += pagerender.parse_content( edit_page_data["content"], edit_page_data["markup"] )
        content += "\n</div>\n"

        # Formular der Seite zum ändern wieder dranhängen
        content += self.editor_page( edit_page_data )

        return content

    def save_page( self ):
        "Abspeichern einer editierten Seite"
        if self.session["isadmin"] != 1:
            return "<strong>You can not edit this page! You have no permissions!</strong>"

        content = ""
        update_time = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime() )

        if self.CGIdata.has_key( "trivial" ):
            content += "<p>trivial modifications selected. The side will not archived.</p>"
        else:
            start_time = time.time()
            old_page_data = self.get_page_data( self.session["edit_page_id"] )

            #~ for k,v in old_page_data.iteritems():
                #~ content += "%s - %s<br>" % (k,v)
            #~ content += "<hr>"

            archiv_data = {
                "userID"    : self.session["user_id"],
                "type"      : "PyLucid,page",
                "date"      : update_time,
                "content"   : pickle.dumps( old_page_data )
            }
            if self.CGIdata.has_key( "summary" ):
                archiv_data["comment"] = self.CGIdata["summary"]

            self.db.insert( "archive", archiv_data )

            end_time = time.time()

            content += "<p>Archived old Sidedata in %.4fsec.</p>" % (end_time - start_time)

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
        new_page_data["lastupdatetime"] = update_time
        new_page_data["lastupdateby"]   = self.session["user_id"]

        start_time = time.time()
        self.db.update(
                table   = "pages",
                data    = new_page_data,
                where   = ("id",self.session["edit_page_id"]),
                limit   = 1
            )
        end_time = time.time()

        content += "<p>Side data updated in %.4fsec.</p>" % (end_time - start_time)

        content += '<a href="%s?%s">to the updated side</a>' % (
                config.system.poormans_url,self.CGIdata["name"]
            )

        return content














