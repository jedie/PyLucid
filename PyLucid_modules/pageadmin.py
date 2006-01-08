#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Alles was mit dem ändern von Inhalten zu tun hat:
    -edit_page
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.3.1"

__history__="""
v0.3.1
    - "CGI_dependent_actions" bei new_page waren falsch.
v0.3
    - page_edit/save nutzt nun die allgemeine Archivierungs Methode archive_page()
    - Vereinheitlichung bei den HTML-Form-Buttons
    - Ob eine neue Seite angelegt werden soll, oder eine bestehende nur editiert wird, erkennt
        das Skript nun an der Page-ID und nicht mehr aus den Session-Daten.
    - Trennung zwischen normalem editieren/speichern und neu/speichern
v0.2
    - NEU: "sequencing" - Ändern der Seiten-Reihenfolge
    - select_del_page benutzt nun CGI_dependent_actions (vereinheitlichung im Ablauf mit anderen Modulen)
v0.1.1
    - NEU: select_edit_page: Editieren einer Seite mit Select-Box in denen _alle_ Seiten angezeigt werden.
    - Bug 1275807 gefixed: "showlinks" und "permitViewPublic" werden nun richtig auf 0 gesetzt statt ""
v0.1.0
    - NEU: Das löschen von Seiten geht nun auch ;)
    - Anpassung an neuen Module-Manager
    - Beim erstellen einer neuen Seite, wird direkt zu dieser "hingesprungen"
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
import sys, cgi, time, pickle, urllib






class pageadmin:
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
        self.parser         = PyLucid["parser"]
        self.render         = PyLucid["render"]
        self.URLs           = PyLucid["URLs"]

    def new_page(self):
        "Neue Seite soll angelegt werden"

        self.page_msg("neue seite!")
        self.page_msg(dir(self.db.cursor))

        core = self.preferences["core"] # Basiseinstellungen

        page_data = {
            "parent"            : int(self.CGIdata["page_id"]),
            "page_id"           : -1, # Damit man beim speichern weiß, das die Seite neu ist.
            "name"              : "Newsite",
            "title"             : "Newsite",
            "template"          : core["defaultTemplate"],
            "style"             : core["defaultStyle"],
            "markup"            : core["defaultMarkup"],
            "showlinks"         : core["defaultShowLinks"],
            "permitViewPublic"  : core["defaultPermitPublic"],
            "ownerID"           : self.session["user_id"],
            "permitViewGroupID" : 1,
            "permitEditGroupID" : 1,
            "content"           : "",
            "keywords"          : "",
            "description"       : "",
        }
        self.editor_page( page_data )

    def get_page_data( self, page_id ):
        """
        Liefert alle Daten die zum editieren einer Seite notwendig sind zurück
        wird auch von self.archive_page() verwendet
        """
        return self.db.page_items_by_id(
            item_list   = ["parent", "name", "title", "template", "style",
                            "markup", "content", "keywords", "description",
                            "showlinks", "permitViewPublic", "permitViewGroupID",
                            "ownerID", "permitEditGroupID"],
            page_id     = page_id
        )

    #_______________________________________________________________________
    # Edit a page

    def select_edit_page(self):
        """
        Wenn eine Seite showlinks ausgeschaltet hat, kommt sie nicht mehr im Menü und
        im siteMap vor. Um sie dennoch editieren zu können, kann man es hierrüber erledigen ;)

        *Wichtig* "url" darf keine Modulemaneger Link nutzen, weil page_id= schon
        enthalten ist. Dieser wird jedoch von der select-Box bestimmt!!!
        """

        return self.db.get_internal_page(
            internal_page_name = "select_edit_page",
            page_dict={
                "url"         : "%s?command=pageadmin&action=edit_page" % self.config.system.real_self_url,
                "site_option" : self.tools.forms().siteOptionList( with_id = True, select = self.CGIdata["page_id"] )
            }
        )

    def edit_page(self, encode_from_db=False):
        page_id = self.CGIdata["page_id"]
        page_data = self.get_page_data( page_id )
        page_data["page_id"] = page_id

        status_msg = "" # Nachricht für encodieren

        if encode_from_db:
            # Daten aus der DB sollen convertiert werden
            encoding = self.CGIdata["encoding"]

            try:
                page_data["content"] = page_data["content"].decode( encoding ).encode( "utf8" )
                status_msg = "<h3>[Encoded from DB with '%s']</h3>" % encoding
            except Exception, e:
                status_msg = "<h3>%s</h3>" % e

        self.editor_page( page_data, status_msg )

    def editor_page( self, edit_page_data, status_msg="" ):
        #~ print "Content-type: text/html\n\n<pre>"
        #~ for k,v in edit_page_data.iteritems(): print k," - ",v," ",cgi.escape( str(type(v)) )
        #~ print "</pre>"
        #~ self.CGIdata.debug()

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

        encoding_option = MyOptionMaker.build_from_list(["utf8","iso-8859-1"], "utf8")

        markup_option   = MyOptionMaker.build_from_list(
            self.db.get_available_markups(),
            self.db.get_markup_id(edit_page_data["markup"])
        )

        parent_option = self.tools.forms().siteOptionList( select=int(edit_page_data["parent"]) )


        def make_option( table_name, select_item ):
            """ Speziallfall: Select Items sind immer "id" und "name" """
            return MyOptionMaker.build_from_dict(
                data            = self.db.select( ("id","name"), table_name ),
                value_name      = "id",
                txt_name        = "name",
                select_item     = select_item
            )

        template_option             = make_option( "templates", edit_page_data["template"] )
        style_option                = make_option( "styles",    edit_page_data["style"] )
        ownerID_option              = make_option( "md5users",  edit_page_data["ownerID"] )
        permitEditGroupID_option    = make_option( "groups",    edit_page_data["permitEditGroupID"] )
        permitViewGroupID_option    = make_option( "groups",    edit_page_data["permitViewGroupID"] )

        if edit_page_data["content"] == None:
            # Wenn eine Seite mit lucidCMS frisch angelegt wurde und noch kein
            # Text eingegeben wurde, ist "content" == None -> Das Produziert
            # beim cgi.escape( edit_page_data["content"] ) einen traceback :(
            # und so nicht:
            edit_page_data["content"] = ""

        #~ edit_page_data["content"] += "\n\n" + str( edit_page_data )
        #~ form_url = "%s?command=pageadmin&page_id=%s" % ( self.config.system.real_self_url, self.CGIdata["page_id"] )
        #~ self.page_msg( edit_page_data )

        self.db.print_internal_page(
            internal_page_name = "edit_page",
            page_dict = {
                "status_msg"                : status_msg, # Nachricht beim encodieren
                # Textfelder
                "url"                       : self.URLs["main_action"],
                "abort_url"                 : self.URLs["base"],
                "page_id"                   : edit_page_data["page_id"],
                "summary"                   : edit_page_data["summary"],
                "name"                      : cgi.escape( edit_page_data["name"] ),
                "title"                     : cgi.escape( edit_page_data["title"] ),
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
        )

    def _set_default( self, dictionary ):
        """
        Kompletiert evtl. nicht vorhandene Keys.
        Leere HTML-input-Felder bzw. nicht aktivierte checkboxen erscheinen nicht in den CGIdaten,
        diese müßen aber für die Weiterverarbeitung im Dict vorhanden sein.
        Diese Methode wird beim Preview und beim speichern benötigt.
        """
        default_dict = {
            "name":"", "title":"", "content":"", "keywords":"", "description":"",
            "showlinks":0, "permitViewPublic":0
        }
        for key, value in default_dict.iteritems():
            if not dictionary.has_key( key ):
                dictionary[key] = value
        return dictionary

    def preview(self, page_id):
        "Preview einer editierten Seite"

        # CGI-Daten holen und leere Form-Felder "einfügen"
        edit_page_data = self._set_default( self.CGIdata )

        edit_page_data["page_id"] = page_id

        # CGI daten sind immer vom type str, die parent ID muß allerdings eine Zahl sein.
        # Ansonsten wird in MyOptionMaker.build_html_option() kein 'selected'-Eintrag gesetzt :(
        edit_page_data["parent"] = int( edit_page_data["parent"] )

        # Preview der Seite erstellen
        print "\n<h3>edit preview:</h3>\n"
        print '<div id="page_edit_preview">\n'

        # Möchte der rendere gern wissen ;)
        edit_page_data['lastupdatetime'] = "now"

        # Alle Tags ausfüllen und Markup anwenden
        print self.render.render( edit_page_data )

        print "\n</div>\n"

        # Formular der Seite zum ändern wieder dranhängen
        self.editor_page( edit_page_data )

    #_______________________________________________________________________
    # SAVE

    def save(self, page_id):
        """Abspeichern einer editierten Seite"""

        # Daten, aufbereitet, holen
        page_data = self._get_edit_data()

        # Archivieren der alten Daten
        if self.CGIdata.has_key("trivial"):
            self.page_msg("trivial modifications selected. Old site is not archived.")
        else:
            if self.CGIdata.has_key("summary"):
                comment = self.CGIdata["summary"]
            else:
                comment = ""

            try:
                self.archive_page(page_id, "old page data", comment)
            except Exception, e:
                self.page_msg("Can't archive old site data: '%s'" % e)
            else:
                self.page_msg("Archived old sitedata.")

        # Daten speichern
        try:
            self.db.update(
                    table   = "pages",
                    data    = page_data,
                    where   = ("id",page_id),
                    limit   = 1
                )
        except Exception, e:
            print "<h3>Error to update site data: '%s'</h3>" % e

        self.page_msg( "New site data updated." )

    def save_new(self):
        """ Abspeichern einer neu erstellten Seite """
        page_data = self._get_edit_data()

        try:
            self.db.insert(
                    table   = "pages",
                    data    = page_data,
                )
        except Exception, e:
            print "<h3>Error to insert new site:'%s'</h3><p>Use browser back botton!</p>" % e

        # Setzt die aktuelle Seite auf die neu erstellte. Das herrausfinden der ID ist
        # nicht ganz so einfach, weil Seitennamen doppelt vorkommen können. Allerdings
        # ist es doch sehr unwahrscheinlich das auch "lastupdatetime" doppelt ist...
        # Na, und wenn schon, dann wird halt die erste genommen ;)
        try:
            self.CGIdata["page_id"] = self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = [
                    ("name", page_data["name"]),
                    ("lastupdatetime", page_data["lastupdatetime"])
                ]
            )[0]["id"]
        except Exception, e:
            print "Can't get ID from new created page?!?! Error: %s" % e

        self.page_msg( "New site saved." )

    def _get_edit_data(self):
        """
        Liefert Daten für das speichern einer editierten und einer neu erstellen Seite.
        """
        # CGI-Daten holen und leere Form-Felder "einfügen"
        CGIdata = self._set_default( self.CGIdata )

        item_list = (
            "parent", "name", "title", "parent", "template", "style",
            "markup", "content", "keywords", "description", "showlinks",
            "permitViewPublic", "permitViewGroupID", "ownerID", "permitEditGroupID"
        )

        # CGI-Daten filtern -> nur Einträge die SeitenInformationen enthalten
        page_data = {}
        for k,v in CGIdata.iteritems():
            if k in item_list:
                page_data[k] = v

        # Daten ergänzen
        page_data["lastupdateby"]   = self.session["user_id"]
        page_data["lastupdatetime"] = self.tools.convert_time_to_sql( time.time() ) # Letzte Änderungszeit

        return page_data

    #_______________________________________________________________________
    # Delete a page

    def select_del_page(self):
        """
        Auswahl welche Seite gelöscht werden soll
        """
        return self.db.get_internal_page(
            internal_page_name = "select_del_page",
            page_dict = {
                "url"         : self.URLs["action"] + "select_del_page",
                "site_option" : self.tools.forms().siteOptionList( with_id = True, select = self.CGIdata["page_id"] )
            }
        )
        self.db.print_internal_TAL_page(
            internal_page_name = "module_admin",
            context_dict = {
                "version"       : __version__,
                "package_data"  : data,
                "installed_data": self.installed_modules_info,
                "action_url"    : self.URLs["action"],
            }
        )

    def delete_page(self, site_id_to_del):
        """
        Löscht die Seite, die ausgewählt wurde
        """
        try:
            comment = self.CGIdata["comment"]
        except KeyError:
            comment = ""

        # Hat die Seite noch Unterseiten?
        parents = self.db.select(
                select_items    = ["name"],
                from_table      = "pages",
                where           = [ ("parent",site_id_to_del) ]
            )
        if parents != ():
            # Hat noch Unterseiten
            msg = "Can't delete Page!"
            self.page_msg( msg )
            print "h3. %s" % msg
            print
            print "Page has parent pages:"
            for site in parents:
                print "* %s" % cgi.escape( site["name"] )
            print "Please move parents."

            # "Menü" wieder anzeigen
            return self.select_del_page()

        try:
            self.archive_page( site_id_to_del, "delete page", comment )
        except Exception, e:
            self.page_msg( "Delete page error:" )
            self.page_msg( "Can't archive site with ID %s: %s" % (site_id_to_del, e) )
            return

        if self.CGIdata["page_id"] == site_id_to_del:
            # Die aktuelle Seite wird gelöscht, also kann sie nicht mehr angezeigt werden.
            # Deswegen gehen wir halt zu parent Seite ;)
            self.CGIdata["page_id"] = self.db.parentID_by_id( site_id_to_del )
            if self.CGIdata["page_id"] == 0:
                # Die oberste Ebene hat ID 0, obwohl es evtl. keine Seite gibt, die ID 0 hat :(
                # Da nehmen wir doch lieber die default-Seite...
                self.CGIdata["page_id"] = self.preferences["core"]["defaultPageName"]

        start_time = time.time()
        self.db.delete(
            table = "pages",
            where = ("id",site_id_to_del),
            limit=1
        )
        duration_time = time.time()-start_time
        self.page_msg(
            "site with ID %s deleted in %.2fsec." % ( site_id_to_del, duration_time )
        )

        # "Menü" wieder anzeigen
        return self.select_del_page()

    #_______________________________________________________________________

    def archive_page( self, page_id, type, comment ):
        """
        Archiviert die Seite mit der ID >page_id<
        Keine Fehlerabfrage, ob Seiten-ID richtig ist!
        """
        start_time = time.time()
        self.db.insert(
            table = "archive",
            data = {
                "userID"    : self.session["user_id"],
                "type"      : type,
                "date"      : self.tools.convert_time_to_sql( time.time() ),
                "comment"   : comment,
                "content"   : pickle.dumps( self.get_page_data( page_id ) )
            }
        )
        duration_time = time.time()-start_time
        self.page_msg(
            "Archived site in %.2fsec." % duration_time
        )

    #_______________________________________________________________________

    def sequencing(self):
        """
        Formular zum ändern der Seiten-Reihenfolge
        """
        MyOptionMaker = self.tools.html_option_maker()

        position_list = [""] + [str(i) for i in xrange(-10,11)]
        position_option = MyOptionMaker.build_from_list( position_list, "" )

        table = '<table id="sequencing">\n'
        for site in self.db.get_sequencing_data():
            table += '<tr>\n'
            table += '  <td class="name">%s</td>\n' % cgi.escape( site["name"] )
            table += '  <td>weight: <strong>%s</strong></td>\n' % site["position"]
            table += '  <td><select name="page_id_%s">%s</select></td>\n' % (site["id"], position_option)
            table += '  </td>\n'
            table += "</tr>\n"
        table += "</table>\n"

        self.db.print_internal_page(
            internal_page_name = "sequencing",
            page_dict = {
                "url"       : self.URLs["action"] + "save_positions",
                "table_data" : table,
            }
        )

    def save_positions(self):
        """
        Positionsänderungen speichern
        """
        #~ self.CGIdata.debug()
        for key,value in self.CGIdata.iteritems():
            if key.startswith("page_id_"):
                try:
                    page_id = int( key[8:] )
                    position = int( value )
                except Exception,e:
                    self.page_msg(
                        "Can't change page position (%s,%s): %s" % (key, value, e)
                    )
                    continue

                self.db.change_page_position( page_id, position)
                self.page_msg( "Save position %s for page with ID %s" % (position,page_id) )

        # Menu wieder anzeigen
        self.sequencing()









