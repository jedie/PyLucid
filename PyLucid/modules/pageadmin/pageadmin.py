#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Alles was mit dem ändern von Inhalten zu tun hat:
    -edit_page
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.4.1"

__history__="""
v0.4.1
    - def tag_list() nutzt nun self.response.startFreshResponse()
v0.4
    - Zeigt nun auch die verfügbaren lucid-Tags/Functions an
v0.3.3
    - Ein sehr übler Fehler bei der Unterscheidung, zwischen dem editieren
        einer bestehenden Seite oder dem anlegen einer neuen Seite.
    - Bugfixes beim erstellen und löschen von Seiten
v0.3.2
    - Änderungen, damit das "encode from DB" besser funktioniert
v0.3.1
    - "CGI_dependent_actions" bei new_page waren falsch.
v0.3
    - page_edit/save nutzt nun die allg. Archivierungs Methode archive_page()
    - Vereinheitlichung bei den HTML-Form-Buttons
    - Ob eine neue Seite angelegt werden soll, oder eine bestehende nur
        editiert wird, erkennt das Skript nun an der Page-ID und nicht mehr
        aus den Session-Daten.
    - Trennung zwischen normalem editieren/speichern und neu/speichern
v0.2
    - NEU: "sequencing" - Ändern der Seiten-Reihenfolge
    - select_del_page benutzt nun CGI_dependent_actions (vereinheitlichung im
        Ablauf mit anderen Modulen)
v0.1.1
    - NEU: select_edit_page: Editieren einer Seite mit Select-Box in denen
        _alle_ Seiten angezeigt werden.
    - Bug 1275807 gefixed: "showlinks" und "permitViewPublic" werden nun
        richtig auf 0 gesetzt statt ""
v0.1.0
    - NEU: Das löschen von Seiten geht nun auch ;)
    - Anpassung an neuen Module-Manager
    - Beim erstellen einer neuen Seite, wird direkt zu dieser "hingesprungen"
v0.0.7
    - "must_admin" für Module-Manager definiert
    - Nutzt Zeitumwandlung aus PyLucid["tools"]
v0.0.6
    - vereinfachung in parent_tree.make_parent_option() durch
        MySQLdb.cursors.DictCursor
v0.0.5
    - NEU: Pseudo Klasse 'module_info' liefert Daten für den Module-Manager
v0.0.4
    - NEU: erstellen einer Seite
v0.0.3
    - NEU: encoding from DB (Daten werden in einem bestimmten Encoding aus
        der DB geholt)
v0.0.2
    - Fehler behoben: parend-ID wird nach einem Preview auf 'root' gesetzt
v0.0.1
    - erste Version
"""

__todo__ = """
"""

# Python-Basis Module einbinden
import sys, cgi, time, pickle, urllib


debug = False
#~ debug = True


from PyLucid.system.BaseModule import PyLucidBaseModule


class pageadmin(PyLucidBaseModule):
    """
    Editieren einer CMS-Seite mit Preview und Archivierung
    """

    def __init__(self, *args, **kwargs):
        super(pageadmin, self).__init__(*args, **kwargs)

        # Der Name, bei dem kein encoding stattfindet (normal Einstellung)
        self.default_code_name = 'default'

    #_______________________________________________________________________
    # Edit a page

    def edit_page(self):
        """
        Einstiegs Methode wenn man auf "edit page" klickt
        """
        if debug:
            from colubrid.debug import debug_info
            self.page_msg(debug_info(self.request))

        if self.request.form.has_key("preview"):
            # Preview der aktuellen Seite
            self.preview()
        elif self.request.form.has_key("save"):
            # Abspeichern der Änderungen
            self.save()
            # Die geänderte Seite soll nach dem speichern angezeigt werden:
            self.session["render follow"] = True
        else:
            # Die aktuelle Seite soll editiert werden
            page_data = self.get_page_data(self.session["page_id"])
            return self.editor_page(page_data)

    def select_edit_page(self):
        """
        Wenn eine Seite showlinks ausgeschaltet hat, kommt sie nicht mehr im
        Menü und im siteMap vor. Um sie dennoch editieren zu können, kann man
        es hierrüber erledigen ;)
        """
        if self.request.form.has_key("page_id"):
            page_id = int(self.request.form["page_id"])
            try:
                page_data = self.get_page_data(page_id)
            except IndexError:
                # Die Seite gibt es nicht!
                self.page_msg("Page '%s' unknown!" % cgi.escape(str(page_id)))
            else:
                self.editor_page(page_data)
                return

        context = {
            "url": self.URLs.actionLink("select_edit_page"),
            "page_option": self.tools.forms().siteOptionList(
                with_id = True, select = self.session["page_id"]
            )
        }

        self.templates.write("select_edit_page", context)

    def editor_page(self, edit_page_data):
        """
        Erstellt die HTML-Seite zum erstellen oder editieren einer Seite
        """
        if str( edit_page_data["showlinks"] ) == "1":
            showlinks = " checked"
        else:
            showlinks = ""

        if str( edit_page_data["permitViewPublic"] ) == "1":
            permitViewPublic = " checked"
        else:
            permitViewPublic = ""

        if not edit_page_data.has_key( "summary"):
            # Information kommt nicht von der Seite,
            # ist aber beim Preview schon vorhanden!
            edit_page_data["summary"] = ""

        MyOptionMaker = self.tools.html_option_maker()

        codecs = self.tools.get_codecs()
        codecs.insert(0, self.default_code_name)

        decode_option = MyOptionMaker.build_from_list(
            codecs,
            select_item=self.request.form.get("decode_from", "")
        )
        encode_option = MyOptionMaker.build_from_list(
            codecs,
            select_item=self.request.form.get("encode_to", "")
        )

        markup_option   = MyOptionMaker.build_from_list(
            self.db.get_available_markups(),
            self.db.get_markup_id(edit_page_data["markup"])
        )

        parent_option = self.tools.forms().siteOptionList(
            select=int(edit_page_data["parent"])
        )


        def make_option( table_name, select_item):
            """ Speziallfall: Select Items sind immer "id" und "name" """
            return MyOptionMaker.build_from_dict(
                data            = self.db.select(("id","name"), table_name),
                value_name      = "id",
                txt_name        = "name",
                select_item     = select_item
            )

        template_option = make_option(
            "templates", edit_page_data["template"]
        )
        style_option = make_option(
            "styles",    edit_page_data["style"]
        )
        ownerID_option = make_option(
            "md5users",  edit_page_data["ownerID"]
        )
        permitEditGroupID_option = make_option(
            "groups",    edit_page_data["permitEditGroupID"]
        )
        permitViewGroupID_option = make_option(
            "groups",    edit_page_data["permitViewGroupID"]
        )

        if edit_page_data["content"] == None:
            # Wenn eine Seite mit lucidCMS frisch angelegt wurde und noch kein
            # Text eingegeben wurde, ist "content" == None -> Das Produziert
            # beim cgi.escape( edit_page_data["content"] ) einen traceback :(
            # und so nicht:
            edit_page_data["content"] = ""

        #~ edit_page_data["content"] += "\n\n" + str( edit_page_data )
        #~ form_url = "%s?command=pageadmin&page_id=%s" % (self.config.system.real_self_url, self.request.form["page_id"] )
        #~ self.page_msg( edit_page_data )

        context = {
            # hidden Felder
            "page_id"                   : edit_page_data["page_id"],
            # URls
            "url"                       : self.URLs.actionLink("edit_page"),
            "list_url"                  : self.URLs.actionLink("tag_list"),
            "abort_url"                 : self.URLs["scriptRoot"],
            # Textfelder
            "summary"                   : edit_page_data["summary"],
            "name"                      : cgi.escape(edit_page_data["name"]),
            "shortcut"                  : edit_page_data["shortcut"],
            "title"                     : cgi.escape(edit_page_data["title"]),
            "keywords"                  : edit_page_data["keywords"],
            "description"               : edit_page_data["description"],
            "content"                   : cgi.escape(edit_page_data["content"]),
            # Checkboxen
            "showlinks"                 : showlinks,
            "permitViewPublic"          : permitViewPublic,
            # List-Optionen
            "decode_option"             : decode_option,
            "encode_option"             : encode_option,
            "markup_option"             : markup_option,
            "parent_option"             : parent_option,
            "template_option"           : template_option,
            "style_option"              : style_option,
            "ownerID_option"            : ownerID_option,
            "permitEditGroupID_option"  : permitEditGroupID_option,
            "permitViewGroupID_option"  : permitViewGroupID_option,
        }

        self.templates.write("edit_page", context)

    def preview(self):
        "Preview einer editierten Seite"

        # CGI-Daten holen und leere Form-Felder "einfügen"
        edit_page_data = self._set_default(self.request.form)

        # CGI daten sind immer vom type str, die parent ID muß allerdings eine
        # Zahl sein. Ansonsten wird in MyOptionMaker.build_html_option() kein
        # 'selected'-Eintrag gesetzt :(
        edit_page_data["parent"] = int(edit_page_data["parent"])

        # Preview der Seite erstellen
        self.response.write("\n<h3>edit preview:</h3>\n")
        self.response.write('<div id="page_edit_preview">\n')

        content = edit_page_data["content"]
        markup = edit_page_data["markup"]
        markup = self.db.get_markup_name(markup)

        # Alle Tags ausfüllen und Markup anwenden
        try:
            content = self.render.apply_markup(content, markup)
        except Exception, e:
            self.response.write("<h4>Can't render preview: %s</h4>" % e)
            self.response.write("<h3>Don't save this changes!</h3>")
        else:
            self.response.write(content)

        self.response.write("\n</div>\n")

        # Formular der Seite zum ändern wieder dranhängen
        self.editor_page( edit_page_data )

    #_______________________________________________________________________
    # new encoding

    def encode_from_db(self, page_id, decode_from=False, encode_to=False):
        """
        FIXME: Obsolete???

        Encodiert den content, nach den aufgewählten Codecs
        """
        def decode_encode(content, codec, method):
            if codec == False or codec==self.default_code_name:
                return content

            if method == "decode":
                msg = "decode from '%s'..." % codec
            else:
                msg = "encode to '%s'..." % codec
            try:
                if method == "decode":
                    content = content.decode(codec)
                else:
                    content = content.encode(codec)
            except Exception, e:
                msg += "Error: %s" % e
            else:
                msg += "OK"

            self.page_msg(msg)

            return content

        page_data = self.get_page_data(page_id)
        page_data["page_id"] = page_id

        # decode
        page_data["content"] = decode_encode(
            page_data["content"], decode_from, "decode"
        )
        # encode
        page_data["content"] = decode_encode(
            page_data["content"], encode_to, "encode"
        )

        self.editor_page(page_data)


    #_______________________________________________________________________
    # SAVE

    def save(self):
        """
        Abspeichern einer neuen oder einer geänderten Seite
        """
        page_data = self._get_edit_data() # Daten, aufbereitet, holen

        page_id = page_data["page_id"]
        # Soll ja nicht in der SQL Tabelle geupdated werden:
        del(page_data["page_id"])

        if page_id == -1:
            # Eine neue Seite muß mit einem INSERT eingefügt werden
            self.insert_new_page(page_data)
        else:
            self.update_page(page_id, page_data)

    def update_page(self, page_id, page_data):
        """Abspeichern einer editierten Seite"""

        # Archivieren der alten Daten
        if self.request.form.has_key("trivial"):
            self.page_msg(
                "trivial modifications selected. Old page is not archived."
            )
        else:
            if self.request.form.has_key("summary"):
                comment = self.request.form["summary"]
            else:
                comment = ""

            try:
                self.archive_page(page_id, "old page data", comment)
            except Exception, e:
                self.page_msg("Can't archive old page data: '%s'" % e)
            else:
                self.page_msg("Archived old pagedata.")

        if page_data["parent"] == page_id:
            # Zur Sicherheit
            self.page_msg(
                "Error in page data. Parent-ID == page_id ! (ID: %s)" % \
                self.session["page_id"]
            )
            return

        # Daten speichern
        try:
            self.db.update(
                    table   = "pages",
                    data    = page_data,
                    where   = ("id",page_id),
                    limit   = 1
                )
        except Exception, e:
            self.page_msg("Error to update page data: %s" % e)
        else:
            self.db.commit()
            self.page_msg("New page data updated.")


    def insert_new_page(self, page_data):
        """ Abspeichern einer neu erstellten Seite """

        try:
            self.db.insert(
                    table   = "pages",
                    data    = page_data,
                )
        except Exception, e:
            msg = (
                "<h3>Error to insert new page:'%s'</h3>\n"
                "<p>Use browser back botton!</p>"
            ) % e
            self.response.write(msg)
        else:
            self.db.commit()
            self.page_msg( "New page saved." )

        # Setzt die aktuelle Seite auf die neu erstellte.
        #~ self.request.form["page_id"] = self.db.cursor.lastrowid
        self.session["page_id"] = self.db.cursor.lastrowid


    def new_page(self):
        "Neue Seite soll angelegt werden"

        core = self.preferences["core"] # Basiseinstellungen

        page_data = {
            "parent"            : self.session["page_id"],

            # Damit man beim speichern weiß, das die Seite neu ist:
            "page_id"           : "-1",

            "name"              : "Newpage",
            "shortcut"          : "",
            "title"             : "Newpage",
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
        self.editor_page(page_data)

    def get_page_data(self, page_id):
        """
        Liefert alle Daten die zum editieren einer Seite notwendig sind zurück
        wird auch von self.archive_page() verwendet
        """
        page_data = self.db.page_items_by_id(
            item_list   = [
                "parent", "name", "shortcut", "title", "template",
                "style", "markup", "content", "keywords", "description",
                "showlinks", "permitViewPublic", "permitViewGroupID",
                "ownerID", "permitEditGroupID"
            ],
            page_id     = page_id
        )
        page_data["page_id"] = page_id
        return page_data


    def _set_default(self, page_data):
        """
        Kompletiert evtl. nicht vorhandene Keys.
        Leere HTML-input-Felder bzw. nicht aktivierte checkboxen erscheinen
        nicht in den CGIdaten, diese müßen aber für die Weiterverarbeitung
        im Dict vorhanden sein. Diese Methode wird beim Preview und beim
        speichern benötigt.
        """
        default_dict = {
            "name":"", "shortcut":"", "title":"", "content":"", "keywords":"",
            "description":"", "showlinks":0, "permitViewPublic":0
        }
        for key, value in default_dict.iteritems():
            if not page_data.has_key(key):
                page_data[key] = value

        if page_data["shortcut"] == "":
            if page_data["name"] != "":
                page_data["shortcut"] = page_data["name"]
            else:
                page_data["shortcut"] = page_data["title"]

        page_data["shortcut"] = self.db.getUniqueShortcut(
            page_data["shortcut"], int(page_data["page_id"])
        )

        return page_data


    def _get_edit_data(self):
        """
        Liefert Daten für das speichern einer editierten und einer neu
        erstellen Seite.
        """
        # CGI-Daten holen und leere Form-Felder "einfügen"
        CGIdata = self.request.form
        CGIdata = self._set_default(CGIdata)

        string_items = (
            "name", "shortcut", "title", "content", "keywords", "description",
        )

        number_items = (
            "page_id", "parent", "parent", "template", "style",
            "markup", "showlinks",
            "permitViewPublic", "permitViewGroupID", "ownerID",
            "permitEditGroupID"
        )
        # CGI-Daten filtern -> nur Einträge die SeitenInformationen enthalten
        page_data = {}
        for k,v in CGIdata.iteritems():
            v = v[0] # Colubrid's MultiDict!
            if k in string_items:
                page_data[k] = v
            elif k in number_items:
                page_data[k] = int(v)

        # Daten ergänzen
        page_data["lastupdateby"] = self.session["user_id"]

        # Letzte Änderungszeit
        page_data["lastupdatetime"] = \
            self.tools.convert_time_to_sql(time.time())

        return page_data

    #_______________________________________________________________________
    # Delete a page

    def select_del_page(self):
        """
        Auswahl welche Seite gelöscht werden soll
        """
        if self.request.form.has_key("page_id_to_del"):
            page_id_to_del = int(self.request.form["page_id_to_del"])
            self.delete_page(page_id_to_del)

        context = {
            "url": self.URLs.actionLink("select_del_page"),
            "page_option": self.tools.forms().siteOptionList(
                with_id = True, select = self.session["page_id"]
            )
        }

        self.templates.write("select_del_page", context)


    def delete_page(self, page_id_to_del):
        """
        Löscht die Seite, die ausgewählt wurde
        """

        comment = self.request.form.get("comment", "")

        # Hat die Seite noch Unterseiten?
        childs = self.db.select(
            select_items    = ["name"],
            from_table      = "pages",
            where           = [ ("parent",page_id_to_del) ]
        )
        if childs:
            # Hat noch Unterseiten
            msg = "Can't delete Page!"
            self.page_msg( msg )
            self.response.write("<h3>%s</h3>\n" % msg)
            self.response.write("<p>Page has child pages:</p><ul>\n")
            for page in childs:
                self.response.write(
                    "<li>%s</li>\n" % cgi.escape(page["name"])
                )
            self.response.write(
                "</ul><p>Please move/delete the child pages first.</p>\n"
            )
            return

        try:
            self.archive_page(page_id_to_del, "delete page", comment)
        except Exception, e:
            self.page_msg("Delete page error:")
            self.page_msg(
                "Can't archive page with ID %s: %s" % (page_id_to_del, e)
            )
            return

        self.session.delete_from_pageHistory(page_id_to_del)
        # Wechselt die Aktuelle Seite zur übergeortneten Seite
        parentID = self.db.parentID_by_id(page_id_to_del)
        self.session["page_id"] = parentID

        start_time = time.time()
        try:
            self.db.delete_page(page_id_to_del)
        except Exception, e:
            self.page_msg(
                "Can't delete page with ID %s: %s" % (page_id_to_del, e)
            )
        else:
            duration_time = time.time()-start_time
            self.page_msg(
                "page with ID %s deleted in %.2fsec." % (
                    page_id_to_del, duration_time
                )
            )

    #_______________________________________________________________________

    def archive_page(self, page_id, type, comment):
        """
        Archiviert die Seite mit der ID >page_id<
        Keine Fehlerabfrage, ob Seiten-ID richtig ist!
        """
        start_time = time.time()
        page_data = self.get_page_data(page_id)
        page_data = pickle.dumps(page_data)
        self.db.insert(
            table = "archive",
            data = {
                "userID"    : self.session["user_id"],
                "type"      : type,
                "date"      : self.tools.convert_time_to_sql(time.time()),
                "comment"   : comment,
                "content"   : page_data,
            }
        )
        duration_time = time.time()-start_time
        self.page_msg(
            "Archived page in %.2fsec." % duration_time
        )

    #_______________________________________________________________________

    def sequencing(self):
        """
        Formular zum ändern der Seiten-Reihenfolge
        """
        if self.request.form.has_key("save"):
            self.save_positions()

        MyOptionMaker = self.tools.html_option_maker()

        position_list = [""] + [str(i) for i in xrange(-10,11)]
        position_option = MyOptionMaker.build_from_list( position_list, "" )

        # Daten in der aktuellen Ebene
        sequencing_data = self.db.get_sequencing_data(self.session["page_id"])

        table = '<table id="sequencing">\n'
        for page in sequencing_data:
            table += '<tr>\n'
            table += '  <td class="name">%s</td>\n' % cgi.escape( page["name"] )
            table += '  <td>weight: <strong>%s</strong></td>\n' % page["position"]
            table += '  <td><select name="page_id_%s">%s</select></td>\n' % (page["id"], position_option)
            table += '  </td>\n'
            table += "</tr>\n"
        table += "</table>\n"

        context = {
            "url"       : self.URLs.currentAction(),
            "table_data" : table,
        }

        self.templates.write("sequencing", context)

    def save_positions(self):
        """
        Positionsänderungen speichern
        """
        for key,value in self.request.form.iteritems():
            if key.startswith("page_id_"):
                try:
                    page_id = int(key[8:])
                except Exception,e:
                    self.page_msg(
                        "Can't get page_id (%s,%s): %s" % (key, value, e)
                    )
                    continue
                try:
                    position = int(value[0])
                except Exception,e:
                    self.page_msg(
                        "Can't get new page position (%s,%s): %s" % (
                            key, value, e
                        )
                    )
                    continue

                self.db.change_page_position( page_id, position)
                self.page_msg(
                    "Save position %s for page with ID %s" % (position,page_id)
                )


    #_________________________________________________________________________

    def tag_list(self):
        """
        Generiert eine Seite mit allen verfügbaren lucid-Tags/Function
        """
        self.response.startFreshResponse()

        tag_list = self.db.get_tag_list()
        #~ self.page_msg(tag_list)
        context = {
            "tag_list": tag_list
        }

        self.templates.write("tag_list", context)

        return self.response







