#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Hier sind alle vorgefertigen Module zu finden, die eigentlich nur
ein normaler SELECT Befehl ist. Also nur Methoden die nur Daten aus
der DB bereitstellen.


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__ = "$Rev$"


import urllib, pickle, sys, time

from PyLucid.system.exceptions import *
from PyLucid.system.DBwrapper.DBwrapper import SQL_wrapper

debug = False

class passive_statements(SQL_wrapper):
    """
    Erweitert den allgemeinen SQL-Wrapper (mySQL.py) um
    spezielle PyLucid-Funktionen.
    """
    #~ def __init__(self, *args, **kwargs):
        #~ super(passive_statements, self).__init__(*args, **kwargs)


    def _error(self, type, txt):
        sys.stderr.write("<h1>SQL error</h1>")
        sys.stderr.write("<h1>%s</h1>" % type)
        sys.stderr.write("<p>%s</p>" % txt)
        sys.exit()

    def _type_error(self, itemname, item):
        import cgi
        item_type = cgi.escape(str(type(item)))
        self._error(
            "%s is not String!" % itemname,
            "It's %s<br/>Check SQL-Table settings!" % item_type
        )

    #_________________________________________________________________________
    ## Direktzugriff auf Tabelleninhalte über db.get_tableDict()

    def internalPageList(self, select_items=None):
        return self.get_tableDict(
            select_items,
            index_key = "name",
            table_name = "pages_internal"
        )

    def pluginsList(self, select_items=["*"]):
        return self.get_tableDict(
            select_items,
            index_key = "id",
            table_name = "plugins"
        )

    def userList(self, select_items=["*"]):
        return self.get_tableDict(
            select_items,
            index_key = "id",
            table_name = "md5users"
        )

    #_________________________________________________________________________
    # Spezielle lucidCMS Funktionen, die von Modulen gebraucht werden

    def get_page_update_info(self, count=10):
        """
        Informationen über die letzten >count< Seiten updates.
        Nutzt: list_of_new_sides und der RSSfeedGenerator
        """
        where_rules = [("showlinks",1)]
        if not self.session.get("isadmin", False):
            # Ist kein Admin -> darf nur öffentliche Seiten sehen.
            where_rules.append(("permitViewPublic",1))

        page_updates = self.select(
            select_items    = [
                "id", "name", "title", "lastupdatetime", "lastupdateby"
            ],
            from_table      = "pages",
            where           = where_rules,
            order           = ( "lastupdatetime", "DESC" ),
            limit           = ( 0, 10 )
        )
        #~ self.page_msg(page_updates)

        # Nur die user aus der DB holen, die auch updates gemacht haben:
        userlist = [item["lastupdateby"] for item in page_updates]
        tmp = {}
        for user in userlist:
            tmp[user] = None
        userlist = tmp.keys()

        where = ["(id=%s)" for i in userlist]
        where = " or ".join(where)

        SQLcommand = "SELECT id,name FROM $$md5users WHERE %s" % where
        users = self.process_statement(SQLcommand, userlist)
        users = self.indexResult(users, "id")

        # Daten ergänzen
        for item in page_updates:
            item["link"] = self.get_page_link_by_id(item["id"])
            item["absoluteLink"] = self.URLs.absoluteLink(item["link"])

            pageName = item["name"]
            pageTitle = item["title"]
            if pageTitle in (None, "", pageName):
                # Eine Seite muß nicht zwingent ein Title haben
                # oder title == name :(
                item["name_title"] = pageTitle
            else:
                item["name_title"] = "%s - %s" % (pageName, pageTitle)

            item["date"] = self.tools.locale_datetime(item["lastupdatetime"])
            user_id = item["lastupdateby"]
            try:
                item["user"] = users[user_id]["name"]
            except KeyError:
                item["user"] = "(unknown userid %s)" % user_id

        return page_updates

    def get_first_page_id(self):
        """
        Liefert die erste existierende page_id zurück
        """
        return self.select(
            select_items    = ["id"],
            from_table      = "pages",
            order           = ("parent","ASC"),
            limit           = 1
        )[0]["id"]

    def get_side_data(self, page_id):
        "Holt die nötigen Informationen über die aktuelle Seite"

        side_data = self.select(
            select_items    = [
                    "markup", "name", "shortcut", "title",
                    "lastupdatetime","keywords","description"
                ],
            from_table      = "pages",
            where           = ( "id", page_id )
        )[0]
        #~ except Exception, e:
            #~ # Vielleicht existiert 'shortcut' noch nicht (Update von v0.6)
            #~ side_data = self.select(
                    #~ select_items    = [
                            #~ "markup", "name", "title",
                            #~ "lastupdatetime","keywords","description"
                        #~ ],
                    #~ from_table      = "pages",
                    #~ where           = ( "id", page_id )
                #~ )

        #~ try:
            #~ side_data = side_data[0]
        #~ except IndexError:
            #~ if page_id == None:
            #~ side_data = {
                #~ "markup": None,
                #~ "lastupdatetime": 0,
            #~ }
            #~ return side_data

        if (not "shortcut" in side_data) or side_data["shortcut"] == "" or \
                                                side_data["shortcut"] == None:
            self.page_msg(
                "ERROR: shortcut for this page is not set!!! "
                "Pages links may not worked! Use LowLevelAdmin to "
                "correct this."
            )
        #~ side_data["template"] = self.side_template_by_id(page_id)

        # None in "" konvertieren
        for key in ("name", "keywords", "description"):
            if (not key in side_data) or side_data[key] == None:
                side_data[key] = ""

        if (not "title" in side_data) or side_data["title"] == None:
            side_data["title"] = side_data["name"]

        return side_data

    def get_shortcutList(self, page_id=None):
        """
        Liefert eine Liste (!) mit allen vorhandenen "shortcuts" zurück.
        Wenn eine page_id angegeben wurde, dann wird dieser shortcut
        herrausgefiltert.
        """
        shortcutList = self.select(
            select_items    = ["id", "shortcut"],
            from_table      = "pages"
        )
        if page_id!=None:
            page_shortcut = None
            for line in shortcutList:
                if line["id"] == page_id:
                    page_shortcut = line["shortcut"]
                    break

        shortcutList = [i["shortcut"] for i in shortcutList]

        if page_shortcut!=None:
            del(
                shortcutList[shortcutList.index(page_shortcut)]
            )

        return shortcutList

    def get_content_and_markup(self, page_id):
        data = self.select(
            select_items    = ["content", "markup"],
            from_table      = "pages",
            where           = ("id", page_id)
        )
        data = data[0]
        data["markup"] = self.get_markup_name(data["markup"])
        return data

    def side_template_by_id(self, page_id):
        """
        Liefert den Inhalt des Template-ID und Templates für die Seite mit
        der >page_id< zurück
        """


        template_id = self.select(
            select_items    = ["template"],
            from_table      = "pages",
            where           = ("id",page_id)
        )
        try:
            template_id = template_id[0]["template"]
        except IndexError:
            #~ if page_id == None:
            # Es existiert keine CMS Seite -> default Template
            template_id = self.preferences["core"]["defaultTemplate"]

        try:
            page_template = self.select(
                    select_items    = ["content"],
                    from_table      = "templates",
                    where           = ("id",template_id)
                )[0]["content"]
        except Exception, e:
            # Fehlerausgabe
            self.page_msg(
                "Can't get Template: %s - Page-ID: %s, Template-ID: %s" % (
                    e, page_id, template_id
                )
            )
            self.page_msg("Please edit the page and change the template!")
            # Bevor garnichts geht, holen wir uns das erst beste Template
            try:
                page_template = self.select(
                        select_items    = ["content"],
                        from_table      = "templates",
                        limit           = (0,1)
                    )[0]["content"]
                return page_template
            except Exception, e:
                # Ist wohl überhaupt nicht's da, dann kommen wir jetzt zum
                # Hardcore Fehlermeldung :(
                self._error(
                    "Can't get Template: %s" % e,
                    "Page-ID: %s, Template-ID: %s" % (page_id, template_id)
                )

        if not isinstance(page_template, basestring):
            self._type_error("Template-Content", page_template)

        return page_template

    def side_id_by_name(self, page_name):
        "Liefert die Side-ID anhand des >page_name< zurück"
        result = self.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ("name",page_name)
            )
        if not result:
            return False

        if "id" in result[0]:
            return result[0]["id"]
        else:
            return False

    def side_name_by_id(self, page_id):
        "Liefert den Page-Name anhand der >page_id< zurück"
        return self.select(
                select_items    = ["name"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["name"]

    def parentID_by_name(self, page_name):
        """
        liefert die parend ID anhand des Namens zurück
        """
        # Anhand des Seitennamens wird die aktuelle SeitenID und den ParentID ermittelt
        return self.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("name",page_name)
            )[0]["parent"]

    def parentID_by_id(self, page_id):
        """
        Die parent ID zur >page_id<
        """
        return self.select(
            select_items    = ["parent"],
            from_table      = "pages",
            where           = ("id",page_id)
        )[0]["parent"]

    def side_title_by_id(self, page_id):
        "Liefert den Page-Title anhand der >page_id< zurück"
        return self.select(
                select_items    = ["title"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["title"]

    def side_style_by_id(self, page_id, getItems):
        "Liefert die CSS-ID und CSS für die Seite mit der >page_id< zurück"
        def get_id(page_id):
            return self.select(
                    select_items    = ["style"],
                    from_table      = "pages",
                    where           = ("id",page_id)
            )[0]["style"]
        try:
            CSS_id = get_id(page_id)
        except (IndexError, KeyError):
            # Beim löschen einer Seite kann es zu einem KeyError kommen
            self.page_msg(
                "Index Error with page_id = %s" % page_id
            )
            try:
                # versuchen wir es mit dem parent
                CSS_id = get_id(self.parentID_by_id(page_id))
                self.page_msg(
                    "Use the styles from parent page!"
                )
            except (IndexError, KeyError):
                # Letzter Versuch
                CSS_id = get_id(self.get_first_page_id())
                self.page_msg(
                    "Use the styles from the first page!"
                )

        data = self.get_style_data(CSS_id, getItems)

        return data

    def get_page_data_by_id(self, page_id):
        "Liefert die Daten zum Rendern der Seite zurück"
        data = self.select(
                select_items    = ["content", "markup"],
                from_table      = "pages",
                where           = ("id", page_id)
            )[0]

        data = self.None_convert(data, ("content",), "")

        return data

    def page_items_by_id(self, item_list, page_id):
        "Allgemein: Daten zu einer Seite"
        page_items = self.select(
            select_items    = item_list,
            from_table      = "pages",
            where           = ("id", page_id)
        )
        page_items = page_items[0]
        for i in ("name", "title", "content", "keywords", "description"):
            if i in page_items and page_items[i]==None:
                page_items[i]=""
        return page_items

    def get_sitemap_data(self):
        """ Alle Daten die für`s Sitemap benötigt werden """
        return self.select(
                select_items    = ["id","name","shortcut","title","parent"],
                from_table      = "pages",
                where           = [("showlinks",1), ("permitViewPublic",1)],
                order           = ("position","ASC"),
            )

    def get_sequencing_data(self, page_id):
        """ Alle Daten die für pageadmin.sequencing() benötigt werden """
        parend_id = self.parentID_by_id(page_id)
        return self.select(
            select_items    = ["id","name","title","parent","position"],
            from_table      = "pages",
            where           = ("parent", parend_id),
            order           = ("position","ASC"),
        )

    #_________________________________________________________________________
    ## Preferences

    def get_all_preferences(self):
        """
        Liefert Daten aus der Preferences-Tabelle
        wird in PyLucid_system.preferences verwendet
        """
        return self.select(
            select_items    = ["section", "varName", "value"],
            from_table      = "preferences",
        )

    def get_one_preference(self, section, varName, select_items=["*"]):
        return self.select(
            select_items,
            from_table      = "preferences",
            where           = [("section",section), ("varName",varName)]
        )[0]

    #_________________________________________________________________________
    ## Funktionen für Styles, Templates usw.

    def get_style_list(self, getItems = ("id","name","description")):
        return self.select(
            select_items    = getItems,
            from_table      = "styles",
            order           = ("name","ASC"),
        )

    def get_stylename_by_id(self, id):
        return self.select(
            select_items    = "name",
            from_table      = "styles",
            where           = ("id", id)
        )[0]["name"]


    def get_style_id_by_name(self, style_name):
        return self.select(
            select_items    = "id",
            from_table      = "styles",
            where           = ("name", style_name)
        )[0]["id"]

    def get_stylenames(self):
        stylenames = self.select(
            select_items    = ["name"],
            from_table      = "styles",
        )
        result = [i["name"] for i in stylenames]
        return result

    def get_UniqueStylename(self, styleName):
        styleNameList = self.get_stylenames()
        uniqueStyleName = self.tools.getUniqueShortcut(
            styleName, styleNameList, strip=False
        )
        return uniqueStyleName

    def get_style_data(
        self, style_id,
        getItems = ("name","description","content")
    ):
        data = self.select(
            select_items    = getItems,
            from_table      = "styles",
            where           = ("id", style_id)
        )[0]
        return data

    def get_style_data_by_name(self, style_name):
        return self.select(
            select_items    = ["description","content"],
            from_table      = "styles",
            where           = ("name", style_name)
        )[0]

    def get_template_list(self):
        return self.select(
                select_items    = ["id","name","description"],
                from_table      = "templates",
                order           = ("name","ASC"),
            )

    def get_templatename_by_id(self, id):
        return self.select(
            select_items    = "name",
            from_table      = "templates",
            where           = ("id", id)
        )[0]["name"]

    def get_template_id_by_name(self, template_name):
        return self.select(
            select_items    = "id",
            from_table      = "templates",
            where           = ("name", template_name)
        )[0]["id"]

    def get_template_data(self, template_id):
        try:
            template_id = int(template_id)
        except:
            raise IndexError, "Template ID is not a number!"

        return self.select(
            select_items    = ["name","description","content"],
            from_table      = "templates",
            where           = ("id", template_id)
        )[0]

    def get_template_data_by_name(self, template_name):
        data = self.select(
            select_items    = ["description","content"],
            from_table      = "templates",
            where           = ("name", template_name)
        )
        data = data[0]
        return data

    def get_templatenames(self):
        names = self.select(
            select_items    = ["name"],
            from_table      = "templates",
        )
        result = [i["name"] for i in names]
        return result

    def get_UniqueTemplatename(self, templateName):
        templateNameList = self.get_templatenames()
        uniqueName = self.tools.getUniqueShortcut(
            templateName, templateNameList, strip=False
        )
        return uniqueName

    #_________________________________________________________________________
    ## InterneSeiten


    #~ def get_internal_page_list(self):
        #~ return self.select(
            #~ select_items    = [
                #~ "name","plugin_id","description",
                #~ "markup","template_engine","markup"
            #~ ],
            #~ from_table      = "pages_internal",
        #~ )

    #~ def get_internal_page_dict(self):
        #~ page_dict = {}
        #~ for page in self.get_internal_page_list():
            #~ page_dict[page["name"]] = page
        #~ return page_dict

    #~ def get_internal_category(self):
        #~ return self.select(
                #~ select_items    = ["id","module_name"],
                #~ from_table      = "plugins",
                #~ order           = ("module_name","ASC"),
            #~ )

    def get_template_engine_name(self, id):
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
            self.page_msg(
                "Warning: Can't get ID for template engine namend '%s'" % name
            )
            return None

    def get_internal_page_data(self, internal_page_name, select_items=None):

        if not select_items:
            # Default Werte setzten
            select_items = [
                "content_html", "content_css", "content_js", "template_engine",
                "markup", "description"
            ]

        data = self.select(select_items,
            from_table      = "pages_internal",
            where           = ("name", internal_page_name)
        )
        try:
            data = data[0]
        except IndexError:
            msg = "Internal page %s not found in db!" % internal_page_name
            raise IndexError, msg

        #~ if replace==True:
            #~ data["template_engine"] = self.get_template_engine(
                #~ data["template_engine"]
            #~ )
            #~ data["markup"] = self.get_markup_name(data["markup"])

        return data

    #~ def get_internal_page(self, internal_page_name, page_dict={}):
        #~ """
        #~ Interne Seite aufgeüllt mit Daten ausgeben. Diese Methode sollte immer
        #~ verwendet werden, weil sie eine gescheite Fehlermeldung anzeigt.
        #~ """
        #~ internal_page = self.get_internal_page_data(internal_page_name)

        #~ try:
            #~ internal_page["content"] = internal_page["content"] % page_dict
        #~ except KeyError, e:
            #~ import re
            #~ placeholder = re.findall(r"%\((.*?)\)s", internal_page["content"])
            #~ raise KeyError(
                #~ "KeyError %s: Can't fill internal page '%s'. \
                #~ placeholder in internal page: %s given placeholder for that page: %s" % (
                    #~ e, internal_page_name, placeholder, page_dict.keys()
                #~ )
            #~ )
        #~ return internal_page


    #~ def get_internal_page_category_id(self, category_name):
        #~ """
        #~ Liefert die ID anhand des Kategorie-Namens zurück
        #~ Existiert die Kategorie nicht, wird sie in die Tabelle eingefügt.
        #~ """
        #~ try:
            #~ return self.select(
                #~ select_items    = ["id"],
                #~ from_table      = "pages_internal_category",
                #~ where           = ("name", category_name)
            #~ )[0]["id"]
        #~ except IndexError:
            #~ # Kategorier existiert noch nicht -> wird erstellt
            #~ self.insert(
                #~ table = "pages_internal_category",
                #~ data  = {"name": category_name}
            #~ )
            #~ return self.cursor.lastrowid

    #_________________________________________________________________________
    ## Userverwaltung

    def _get_userdata(self, where, select_items):
        """
        Generische Methode für die Userdaten-Methoden
        """
        data = self.select(
            select_items    = select_items,
            from_table      = "md5users",
            where           = where,
            limit           = 1,
        )[0]
        return data

    def get_userdata_by_md5username(self, md5username, select_items=["*"]):
        """
        Generische Methode um Userdaten anhand des md5username zu bekommen
        """
        where           = ("username_md5", md5username)
        return self._get_userdata(where, select_items)

    def get_userdata_by_username(self, username, select_items=["*"]):
        """
        Generische Methode um Userdaten anhand des normalen Username zu
        bekommen
        """
        where = ("name", username)
        return self._get_userdata(where, select_items)

    def get_userdata_by_userid(self, userid, select_items=["*"]):
        """
        Generische Methode um Userdaten anhand des normalen Username zu
        bekommen
        """
        where = ("id", userid)
        return self._get_userdata(where, select_items)

    def get_all_userdata(self, select_items=["*"]):
        data = self.select(
            select_items    = select_items,
            from_table      = "md5users",
        )
        return data

    #~ def normal_login_userdata(self, username):
        #~ "Userdaten die bei einem normalen Login benötigt werden"
        #~ return self.select(
                #~ select_items    = ["id", "password", "admin"],
                #~ from_table      = "md5users",
                #~ where           = ("name", username)
            #~ )[0]

    #~ def userdata(self, username):
        #~ return self.select(
                #~ select_items    = ["id", "name","realname","email","admin"],
                #~ from_table      = "md5users",
                #~ where           = ("name", username)
            #~ )[0]

    #~ def md5_login_userdata(self, username):
        #~ "Userdaten die beim JS-md5 Login benötigt werden"
        #~ return self.select(
                #~ select_items    = ["id", "pass1", "pass2", "admin"],
                #~ from_table      = "md5users",
                #~ where           = ("name", username)
            #~ )[0]

    #~ def exists_admin(self):
        #~ """
        #~ Existiert schon ein Admin?
        #~ """
        #~ result = self.select(
            #~ select_items    = ["id"],
            #~ from_table      = "md5users",
            #~ limit           = (1,1)
        #~ )
        #~ if result:
            #~ return True
        #~ else:
            #~ return False

    #~ def user_data_list(self):
        #~ """ wird in userhandling verwendet """
        #~ return self.select(
            #~ select_items = ["id","name","realname","email","admin"],
            #~ from_table = "md5users"
        #~ )

    #~ def user_info_by_id(self, id):
        #~ return self.select(
            #~ select_items    = ["id","name","realname","email","admin"],
            #~ from_table      = "md5users",
            #~ where           = ("id", id)
        #~ )[0]

    #_________________________________________________________________________
    ## Module / Plugins

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

        #~ def unpickle(SQL_result_list):
            #~ for line in SQL_result_list:
                #~ for item in ("CGI_laws", "get_CGI_data"):
                    #~ if line[item] == None:
                        #~ continue
                    #~ try:
                    #~ line[item] = pickle.loads(line[item])
                    #~ except:
            #~ return SQL_result_list

        # Daten der Methode holen
        method_properties = self.select(
            select_items    = [
                "id", "must_login", "must_admin", "menu_section",
                "menu_description", "direct_out", "sys_exit", "has_Tags",
                "no_rights_error"
            ],
            from_table      = "plugindata",
            where           = [
                ("plugin_id", plugin_id), ("method_name",method_name)
            ],
        )
        #~ method_properties = unpickle(method_properties)[0]

        return method_properties[0]

    def get_method_id(self, plugin_id, method_name):
        """ Wird beim installieren eines Plugins benötigt """
        return self.select(
            select_items    = ["id"],
            from_table      = "plugindata",
            where           = [
                ("plugin_id", plugin_id), ("method_name", method_name)
            ],
        )[0]["id"]

    def get_plugin_id(self, package, module):
        """ Wird beim installieren eines Plugins benötigt """
        return self.select(
            select_items    = ["id"],
            from_table      = "plugins",
            where           = [
                ("package_name", package), ("module_name", module)
            ],
        )[0]["id"]

    def get_package_name(self, module_name):
        """ Für PluginDownload """
        return self.select(
            select_items    = ["package_name"],
            from_table      = "plugins",
            where           = ("module_name", module_name),
        )[0]["package_name"]

    def get_plugin_data_by_id(self, plugin_id, select_items=None):
        if not select_items:
            # Default Keys
            select_items = [
                "id", "module_name", "package_name", "SQL_deinstall_commands",
                "active"
            ]

        result = self.select(select_items,
            from_table      = "plugins",
            where           = ("id", plugin_id),
        )[0]
        return result

    def get_installed_modules_info(self):
        """
        Für ModulAdmin und PluginDownload
        """
        return self.select(
            select_items    = [
                "module_name", "package_name", "id","version","author",
                "url","description","active"
            ],
            from_table      = "plugins",
            #~ debug = True,
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
            select_items    = ["method_name", "menu_section", "menu_description"],
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
                "plugin_id", "name", "template_engine", "markup",
                "lastupdatetime", "lastupdateby", "description"
            ],
            from_table      = "pages_internal",
            where           = [("plugin_id", plugin_id)]
        )
        for page_info in pages_info:
            page_info["markup"] = self.get_markup_name(page_info["markup"])
            try:
                page_info["lastupdateby"] = \
                    self.user_info_by_id(page_info["lastupdateby"])["name"]
            except IndexError:
                pass
        return pages_info

    def get_tag_list(self):
        """
        Liefert eine Liste der installieren und aktivierten Tags
        """
        SQLcommand = (
            "SELECT id,module_name,package_name,description"
            " FROM $$plugins"
            " WHERE active!=0;"
        )
        plugin_list = self.process_statement(SQLcommand)
        plugin_dict = self.indexResult(plugin_list, "id")
        #self.page_msg(plugin_dict)

        SQLcommand = (
            "SELECT plugin_id,method_name"
            " FROM $$plugindata"
            " WHERE method_name='lucidTag' OR method_name='lucidFunction';"
        )
        method_list = self.process_statement(SQLcommand)
        #self.page_msg(method_list)

        tag_list = []
        for method in method_list:
            #~ self.page_msg(method)
            plugin_id = method['plugin_id']

            if not plugin_id in plugin_dict:
                # Sollte eigentlich nie vorkommen
                self.page_msg("Warning: obsolete method found!")
                continue

            plugin_data = dict(plugin_dict[plugin_id]) # make a copy

            method_name = method["method_name"]
            if method_name == 'lucidTag':
                plugin_data["is_lucidTag"] = True
            elif method_name == 'lucidFunction':
                plugin_data["is_lucidFunction"] = True

            tag_list.append(plugin_data)

        #self.page_msg(tag_list)
        return tag_list

    #_________________________________________________________________________
    ## LOG

    def get_last_logs(self, limit=10):
        return self.select(
            select_items    = ["timestamp", "sid", "user_name", "domain",
                                                "message", "typ", "status"],
            from_table      = "log",
            order           = ("timestamp","DESC"),
            limit           = (0,limit)
        )

    #_________________________________________________________________________
    ## Rechteverwaltung

    def get_permitViewPublic(self, page_id):
        return self.select(
                select_items    = [ "permitViewPublic" ],
                from_table      = "pages",
                where           = ("id", page_id),
            )[0]["permitViewPublic"]

    #_________________________________________________________________________
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
        return markups

    def get_available_template_engines(self):
        """
        Bildet eine Liste aller verfügbaren template_engines. Jeder Listeneintrag ist wieder
        eine Liste aus [ID,name]. Das ist ideal für tools.html_option_maker().build_from_list()
        """
        engines = self.select(
            select_items    = ["id","name"],
            from_table      = "template_engines",
        )
        return engines

    #_________________________________________________________________________
    ## L10N

    def get_L10N(self, lang, key):
        return self.select(
            select_items    = ["value"],
            from_table      = "l10n",
            where           = [("lang", lang), ("varName",key)]
        )[0]["value"]

    def get_supported_languages(self):
        """
        Liste alle eingerichteten Sprachen
        """
        SQLcommand = "SELECT lang FROM $$l10n GROUP BY lang;"
        languages = self.process_statement(SQLcommand)
        languages = [i["lang"] for i in languages]

        return languages


