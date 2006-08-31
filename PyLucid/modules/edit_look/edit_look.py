#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Editor für alles was mit aussehen zu tun hat:
    - edit_style
    - edit_template
    - edit_internal_page
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.3.1"

__history__="""
v0.3.1
    - Neu: Apply Button bei "edit internal page"
v0.3
    - Anpassung an PyLucid v0.7
v0.2
    - Bug 1308063: Umstellung von <button> auf <input>, weil's der IE nicht
        kann s. http://www.python-forum.de/viewtopic.php?t=4180
    - NEU: Styles und Template könnne nur dann gelöscht werden, wenn keine
        Seite diese noch benutzten
v0.1.1
    - edit_internal_page_form: markups sind nun IDs aus der Tabelle markups
v0.1.0
    - Komplettumbau für neuen Module-Manager
v0.0.4
    - Bug: Internal-Page Edit geht nun wieder
v0.0.3
    - Bug: Edit Template:
        http://sourceforge.net/tracker/index.php?func=detail&aid=1273348&group_id=146328&atid=764837
v0.0.2
    - NEU: Clonen von Stylesheets und Templates nun möglich
    - NEU: Löschen von Stylesheets und Templates geht nun
    - Änderung der "select"-Tabellen, nun Anpassung per CSS möglich
v0.0.1
    - erste Version
"""

__todo__ = """
"""

# Python-Basis Module einbinden
import sys, cgi



from PyLucid.system.BaseModule import PyLucidBaseModule


class StyleAndTemplate(PyLucidBaseModule):
    """
    Methoden für Stylesheet und Template Verwaltung
    """

    def action(self):

        if self.request.form.has_key("edit"):
            self._makeEditPage()
            return
        elif self.request.form.has_key("clone"):
            self._cloneItem()
        elif self.request.form.has_key("del"):
            self._delItem()
        elif self.request.form.has_key("save"):
            self._updateItem()

        # Styles/Templates Auswahl anzeigen:
        self._select_table()


    def _cloneItem(self):
        """ Ein Stylesheet soll kopiert werden """

        clone_name = self.request.form["clone_name"]

        try:
            content = \
                    self.db_getItemDataByName(clone_name)["content"]
        except IndexError:
            msg = "Can't get content from %s '%s'" % (
                self.type, clone_name
            )
            self.page_msg(msg)
            return

        new_name = self.request.form.get("new_name", "%s_copy" % clone_name)
        # Einen evtl. doppelten Namen eindeutig machen (Zahl wird angehängt)
        new_name = self.db_getUniqueItemName(new_name)

        data = {
            "name"          : new_name,
            "description"   : "clone of '%s'" % clone_name,
            "content"       : content,
        }
        try:
            self.db_newItem(data)
        except Exception, e:
            msg = "Error clone %s '%s' to '%s': %s" % (
                self.type, clone_name, new_name, e
            )
        else:
            msg = "%s '%s' duplicated to '%s'" % (
                self.type, clone_name, new_name
            )

        self.page_msg(msg)

    def _updateItem(self):
        """
        Speichert die Änderungen vom template oder stylesheet editieren.
        """
        id = self._getID()
        if id==None: return

        name = self.request.form["name"]
        data = {
            "name": name,
            "description": self.request.form.get("description",""),
            "content": self.request.form["content"]
        }
        try:
            self.db_updateItem(id, data)
        except Exception, e:
            self.page_msg("Can't update %s: %s" % (self.type, e))
        else:
            self.page_msg("%s '%s' saved!" % (self.type, name))


    def _makeEditPage(self):
        """ Erstellt die Seite zum Stylesheet/Template editieren """

        id = self._getID()
        if id==None: return

        try:
            edit_data = self.db_getItemData(id)
        except IndexError:
            self.page_msg("bad style id '%s'!" % id)
            return

        context = {
            "name"          : edit_data["name"],
            "url"           : self.URLs.currentAction(),
            "content"       : cgi.escape( edit_data["content"] ),
            "description"   : cgi.escape( edit_data["description"] ),
            "id"            : id,
        }
        internal_page_name = "edit_%s" % self.type
        self.templates.write(internal_page_name, context)

    def _select_table(self):
        """ Erstellt die Tabelle zum auswählen eines Style/Templates """

        table_data = self.db_getItemList()
        nameList = [i["name"] for i in table_data]

        context = {
            "url": self.URLs.currentAction(),
            "nameList": nameList,
            "itemsDict": table_data,
        }
        internalPageName = "select_%s" % self.type
        self.templates.write(internalPageName, context)

    def _delItem( self ):
        """ Lösche ein Stylesheet """
        id = self._getID()
        if id==None: return

        page_names = self.db.select(
            select_items    = ["name"],
            from_table      = "pages",
            where           = (self.type, id)
        )
        if page_names:
            names = [cgi.escape(i["name"]) for i in page_names]
            msg = (
                "Can't delete %s, the following pages used it:\n"
                "%s"
            ) % (self.type, names)
            self.page_msg(msg)
            return

        try:
            self.db_deleteItem(id)
        except Exception, e:
            msg = "Error deleting %s with id '%s': %s" % (self.type, id, e)
        else:
            msg = "%s with id %s deleted." % (self.type, id)

        self.page_msg(msg)

    def _getID(self):
        try:
            id = self.request.form["id"]
        except KeyError:
            self.page_msg("Error: There is no %s ID in POST data!" % self.type)
            return None

        try:
            id = int(id)
        except:
            self.page_msg("Error: %s ID is not a number!" % self.type)
            return None

        return id


class Style(StyleAndTemplate):
    """
    Namen und Methoden zur Stylesheet Verabreitung
    """
    table_name = "styles"
    type = "style"

    def __init__(self, *args, **kwargs):
        super(Style, self).__init__(*args, **kwargs)

        # Datenbank-Methoden für die Stylesheet Verabreitung definieren die
        # von der Klasse StyleAndTemplate benutzt werden:

        # select
        self.db_getItemList = self.db.get_style_list

        # edit
        self.db_getItemData = self.db.get_style_data

        # save
        self.db_updateItem = self.db.update_style

        # clone
        self.db_newItem = self.db.new_style
        self.db_getItemDataByName = self.db.get_style_data_by_name
        self.db_getUniqueItemName = self.db.get_UniqueStylename

        # delete
        self.db_deleteItem = self.db.delete_style


class Template(StyleAndTemplate):
    """
    Namen und Methoden zur Template Verabreitung
    """
    table_name = "templates"
    type = "template"

    def __init__(self, *args, **kwargs):
        super(Template, self).__init__(*args, **kwargs)

        # Datenbank-Methoden für die Template Verabreitung definieren die
        # von der Klasse StyleAndTemplate benutzt werden:

        # select
        self.db_getItemList = self.db.get_template_list

        # edit
        self.db_getItemData = self.db.get_template_data

        # save
        self.db_updateItem = self.db.update_template

        # clone
        self.db_newItem = self.db.new_template
        self.db_getItemDataByName = self.db.get_template_data_by_name
        self.db_getUniqueItemName = self.db.get_UniqueTemplatename

        # delete
        self.db_deleteItem = self.db.delete_template



class edit_look(PyLucidBaseModule):

    def stylesheet(self):
        """ Es wird die internal_page 'select_style' zusammen gebaut """
        s = Style(self.request, self.response)
        s.action()


    def template(self):
        """ Es wird die internal_page 'select_template' zusammen gebaut """
        t = Template(self.request, self.response)
        t.action()

    #_________________________________________________________________________
    ## Interne Seiten editieren

    def internal_page(self):
        """
        Tabelle zum auswählen einer Internen-Seite zum editieren

        jinja context:

        context = [
            {
                "package":"buildin_plugins",
                "data": [
                    {
                        "module_name":"plugin1",
                        "data": [
                            {"name": "internal page1",
                            ...},
                            {"name": "internal page2",
                            ...},
                        ],
                    {
                        "module_name":"plugin2",
                        "data": [...]
                    },
                ]
            },
            {
                "package":"modules",
                "data": [...]
            }
        ]
        """
        if "save" in self.request.form:
            # Zuvor editierte interne Seite speichern
            self.save_internal_page()
        elif "apply" in self.request.form:
            # Editierte Daten speichern aber wieder den Editor öffnen
            internal_page_name = self.request.form['internal_page_name']
            self.save_internal_page()
            self.edit_internal_page([internal_page_name])
            return

        select_items = [
            "name","plugin_id","description","lastupdatetime","lastupdateby"
        ]
        internal_pages = self.db.internalPageList(select_items)

        select_items = ["id", "package_name", "module_name"]
        plugin_data = self.db.pluginsList(select_items)

        users = self.db.userList(select_items=["id", "name"])
        #~ print users

        # Den ID Benzug auflösen und Daten zusammenfügen
        for page_name, data in internal_pages.iteritems():
            # Username ersetzten. Wenn die Daten noch nie editiert wurden,
            # dann ist die ID=0 und der user existiert nicht in der DB!
            lastupdateby = data["lastupdateby"]
            user = users.get(lastupdateby, {"name":"<em>[nobody]</em>"})
            data["lastupdateby"] = user["name"]

            # Plugindaten
            plugin_id = data["plugin_id"]
            try:
                plugin = plugin_data[plugin_id]
            except KeyError:
                # Plugin wurde schon aus der Db gelöscht, allerdings ist die
                # interne Seite noch da, was nicht richtig ist!
                self.page_msg("orphaned internal page '%s' found!" % page_name)
                #~ del(internal_pages[page_name])
                continue

            data.update(plugin)

        # Baut ein Dict zusammen um an alle Daten über die Keys zu kommen
        contextDict = {}
        for page_name, data in internal_pages.iteritems():
            try:
                package_name = data["package_name"]
            except KeyError:
                # Verwaiste interne Seite, wird ignoriert
                continue
            package_name = package_name.split(".")
            package_name = package_name[1]
            data["package_name"] = package_name
            module_name = data["module_name"]

            if not package_name in contextDict:
                contextDict[package_name] = {}

            if not module_name in contextDict[package_name]:
                contextDict[package_name][module_name] = []

            contextDict[package_name][module_name].append(data)

        # Baut eine Liste für jinja zusammen
        context_list = []
        package_list = contextDict.keys()
        package_list.sort()
        for package_name in package_list:
            package_data = contextDict[package_name]

            plugins_keys = package_data.keys()
            plugins_keys.sort()

            plugin_list = []
            for plugin_name in plugins_keys:
                plugin_data = package_data[plugin_name]

                internal_page_list = []
                for internal_page in plugin_data:
                    module_name = internal_page["module_name"]
                    del(internal_page["module_name"])
                    del(internal_page["package_name"])
                    del(internal_page["plugin_id"])
                    del(internal_page["id"])
                    internal_page_list.append(internal_page)

                internal_page = {
                    "module_name": module_name,
                    "data": internal_page_list
                }
                plugin_list.append(internal_page)

            context_list.append({
                "package_name": package_name,
                "data": plugin_list
            })

        context = {
            "version": __version__,
            "itemsList": context_list,
            #~ "url": self.URLs.currentAction(),
            "url": self.URLs.actionLink("edit_internal_page"),
        }

        # Seite anzeigen
        self.templates.write("select_internal_page", context)

    def edit_internal_page(self, function_info):
        """ Formular zum editieren einer internen Seite """

        internal_page_name = function_info[0]

        try:
            # Daten der internen Seite, die editiert werden soll
            edit_data = self.db.get_internal_page_data(internal_page_name)
        except IndexError:
            msg = (
                "bad internal-page name: '%s' !"
            ) % cgi.escape(internal_page_name)
            self.page_msg(msg)
            self.internal_page() # Auswahl wieder anzeigen lassen
            return

        OptionMaker = self.tools.html_option_maker()
        markup_option = OptionMaker.build_from_list(
            self.db.get_available_markups(), edit_data["markup"],
            select_value=False
        )
        template_engine_option = OptionMaker.build_from_list(
            self.db.get_available_template_engines(),
            edit_data["template_engine"], select_value=False
        )

        context = {
            "name"          : internal_page_name,
            "back_url"      : self.URLs.actionLink("internal_page"),
            "url"           : self.URLs.actionLink("internal_page"),
            "content_html"  : cgi.escape(edit_data["content_html"]),
            "content_css"   : cgi.escape(edit_data["content_css"]),
            "content_js"    : cgi.escape(edit_data["content_js"]),
            "description"            : cgi.escape(edit_data["description"]),
            "template_engine_option" : template_engine_option,
            "markup_option"          : markup_option,
        }

        self.templates.write("edit_internal_page", context)

    def save_internal_page(self):
        """ Speichert einen editierte interne Seite """
        internal_page_name = self.request.form['internal_page_name']

        page_data = self._get_filteredFormDict(
            strings = (
                "content_html", "content_css", "content_js", "description"
            ),
            numbers = ("markup", "template_engine"),
            default = ""
        )

        # HTML abspeichern
        page_data = {
            "lastupdateby"      : self.session['user_id'],
            "content_html"      : page_data["content_html"],
            "content_css"       : page_data.get("content_css",""),
            "content_js"        : page_data.get("content_js",""),
            "description"       : page_data.get("description",""),
            "markup"            : page_data["markup"],
            "template_engine"   : page_data["template_engine"],
        }
        escaped_name = cgi.escape(internal_page_name)
        try:
            self.db.update_internal_page(
                internal_page_name, page_data
            )
        except Exception, e:
            msg = "Error saving code from internal page '%s': %s" % (
                escaped_name, e
            )
        else:
            msg = "code for internal page '%s' saved!" % escaped_name

        self.page_msg(msg)

    #_______________________________________________________________________
    ## Allgemeine Funktionen

    def error( *msg ):
        page  = "<h2>Error.</h2>"
        page += "<p>%s</p>" % "<br/>".join( [str(i) for i in msg] )
        return page

    def _get_filteredFormDict(self, strings=None, numbers=None, default=False):
        result = {}
        for name in strings:
            if default!=False:
                result[name] = self.request.form.get(name, default)
            else:
                result[name] = self.request.form[name]
        for name in numbers:
            result[name] = int(self.request.form[name])

        return result

