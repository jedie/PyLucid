#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Alles was mit dem ändern von Inhalten zu tun hat:
    -edit_page

Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev:$"


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
        if debug: self.debug()

        if "preview" in self.request.form:
            # Preview der aktuellen Seite
            self.preview()
        elif "save" in self.request.form:
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
        if "page_id" in self.request.form:
            page_id = int(self.request.form["page_id"])
            try:
                page_data = self.get_page_data(page_id)
            except IndexError:
                # Die Seite gibt es nicht!
                if page_id == 0:
                    self.page_msg("The virtual page 'root' can't be edit :)")
                else:
                    self.page_msg(
                        "Page '%s' unknown!" % cgi.escape(str(page_id))
                    )
            else:
                self.editor_page(page_data)
                return

        # Generiert eine Liste aller Seiten für einen html-select
        pages_tree = self.tools.parent_tree_maker().make_parent_option()

        context = {
            "url": self.URLs.actionLink("select_edit_page"),
            "pages_tree": pages_tree,
        }
        #~ self.page_msg(context)


        self.templates.write("select_edit_page", context)

    def editor_page(self, edit_page_data):
        """
        Erstellt die HTML-Seite zum erstellen oder editieren einer Seite
        """
        context = edit_page_data

        musthave_keys = (
            "page_id", "summary"
        )
        #~ context["trivial"] = edit_page_data.get("trivial", 0)

        # URLs
        context["url_action"] = self.URLs.actionLink("edit_page")
        context["url_taglist"] = self.URLs.actionLink("tag_list")
        context["url_abort"] = self.URLs.actionLink("scriptRoot")
        context["url_textile_help"] = self.URLs.actionLink("tinyTextile_help")

        # Textfelder
        if context["content"] == None:
            # Wenn eine Seite mit lucidCMS frisch angelegt wurde und noch kein
            # Text eingegeben wurde, ist "content" == None
            context["content"] = ""

        escape_keys = (
            "name", "shortcut", "title", "keywords","description","content"
        )
        for key in escape_keys:
            context[key] = cgi.escape(context[key])

        if isinstance(context["markup"], basestring):
            # Sollte eigentlich die ID des Markups sein!
            markup_id = self.db.get_markup_id(context["markup"])
            context["markup"] = markup_id


        int_keys = (
            "markup", "ownerID", "page_id", "parent",
            "permitEditGroupID", "permitViewGroupID",
            "style", "template"
        )
        for key in int_keys:
            try:
                context[key] = int(context[key])
            except KeyError, key:
                self.page_msg.red("Form Error: Key '%s' not found!" % key)
                return

        def get_name_and_id(table_name):
            return self.db.select(("id","name"), table_name)

        # List-Optionen
        context["markups"] = get_name_and_id("markups")
        context["templates"] = get_name_and_id("templates")
        context["styles"] = get_name_and_id("styles")
        context["users"] = get_name_and_id("md5users")

        parent_data = self.tools.parent_tree_maker().make_parent_option()
        context["parent_data"] = parent_data

        #~ self.page_msg(context)
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

        #~ self.page_msg(page_data)
        #~ self.page_msg(self.request.form)

        # Archivieren der alten Daten
        if "trivial" in self.request.form:
            self.page_msg(
                "trivial modifications selected. Old page is not archived."
            )
        else:
            comment = self.request.form.get("summary", "")

            try:
                self.archive_page(page_id, "old page data", comment)
            except Exception, e:
                self.page_msg("Can't archive old page data: '%s'" % e)
            else:
                self.page_msg("Archived old pagedata.")

        if page_data["parent"] == page_id:
            # Zur Sicherheit
            # ToDo: Müßte auch andere ungültige Angaben überprüfen
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

        #~ try:
        self.db.insert(
            table   = "pages",
            data    = page_data,
        )
        #~ except Exception, e:
            #~ msg = (
                #~ "<h3>Error to insert new page:'%s'</h3>\n"
                #~ "<p>Use browser back botton!</p>"
            #~ ) % e
            #~ self.response.write(msg)
        #~ else:

        self.db.commit()
            #~ self.page_msg( "New page saved." )

        # Setzt die aktuelle Seite auf die neu erstellte.
        self.session["page_id"] = self.db.cursor.lastrowid


    def new_page(self):
        "Neue Seite soll angelegt werden"
        new_page_data = self.get_new_page_data()

        # Damit man beim speichern weiß, das die Seite neu ist:
        new_page_data["page_id"] = "-1"

        self.editor_page(new_page_data)

    def get_new_page_data(self):
        """
        Liefert ein dict mit allen nötigen Werten zurück, damit der page_editor
        die "Neue Seite Anlegen" Anzeigen kann
        """
        core = self.preferences["core"] # Basiseinstellungen

        parent = self.session["page_id"]
        if parent == None:
            # Es gibt noch keine andere Seite
            parent = 0

        page_data = {
            "parent"            : parent,
            "name"              : "Newpage",
            "shortcut"          : "",
            "title"             : "Newpage",
            "template"          : core["defaultTemplate"],
            "style"             : core["defaultStyle"],
            "markup"            : self.preferences.get_default_markup_id(),
            "showlinks"         : core["defaultShowLinks"],
            "permitViewPublic"  : core["defaultPermitPublic"],
            "ownerID"           : self.session.get("user_id",0),
            "permitViewGroupID" : 1,
            "permitEditGroupID" : 1,
            "content"           : "",
            "keywords"          : "",
            "description"       : "",
        }
        return page_data

    def create_first_page(self):
        """
        In der db existiert noch keine CMS Seite, diese soll nun automatisch
        angelegt werden, damit PyLucid überhaupt funktioniert.
        Wird von PyLucid_app.py aufgerufen.
        """
        new_page_data = self.get_new_page_data()
        new_page_data["shortcut"]   = "Newpage"
        new_page_data["parent"]     = 0
        self.insert_new_page(new_page_data)

    def get_page_data(self, page_id):
        """
        Liefert alle Daten die zum editieren einer Seite notwendig sind zurück
        wird auch von self.archive_page() verwendet
        """
        page_data = self.db.page_items_by_id(
            item_list   = ["*"],
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
            "name":"", "shortcut":"", "title":"",
            "content":"", "keywords":"", "description":"",
            "showlinks":0, "permitViewPublic":0,
        }

        for key, value in default_dict.iteritems():
            if not key in page_data:
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
            "page_id", "parent",
            "template", "style", "markup",
            "showlinks", "permitViewPublic",
            "permitViewGroupID", "permitEditGroupID", "ownerID",
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
        if "page_id_to_del" in self.request.form:
            page_id_to_del = int(self.request.form["page_id_to_del"])
            self.delete_page(page_id_to_del)

        # Generiert eine Liste aller Seiten für einen html-select
        pages_tree = self.tools.parent_tree_maker().make_parent_option()

        context = {
            "url": self.URLs.actionLink("select_del_page"),
            "pages_tree": pages_tree,
        }
        #~ self.page_msg(context)
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

    def tinyTextile_help(self):
        """
        tinyTextile Hilfe Seite ausgeben
        """
        self.response.startFreshResponse()
        self.templates.write("tinyTextile_help", context={})
        return self.response

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
        if "save" in self.request.form:
            self.save_positions()

        # Daten in der aktuellen Ebene
        sequencing_data = self.db.get_sequencing_data(self.session["page_id"])

        context = {
            "url"       : self.URLs.currentAction(),
            "sequencing_data" : sequencing_data,
            "weights"   : [i for i in xrange(-10,11)]
        }
        #~ self.page_msg(context)
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







