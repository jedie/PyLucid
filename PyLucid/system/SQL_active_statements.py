#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

"""
Alle vorgefertigten Methoden, die aktiv Daten in der DB verändern und
über einfache SELECT Befehle hinausgehen
"""

__version__="0.1"

__history__="""
v0.1
    - erste Release
"""

import pickle, sys, time

from PyLucid.system.SQL_passive_statements import passive_statements
from PyLucid.system.exceptions import *

debug = False

class active_statements(passive_statements):
    """
    Erweitert den allgemeinen SQL-Wrapper (mySQL.py) um
    spezielle PyLucid-Funktionen.
    """
    #~ def __init__(self, *args, **kwargs):
        #~ super(active_statements, self).__init__(*args, **kwargs)



    #_________________________________________________________________________

    def get_page_link_by_id(self, page_id):
        """ Generiert den absolut-Link zur Seite """
        data = []

        while page_id != 0:
            result = self.select(
                    select_items    = ["shortcut","parent"],
                    from_table      = "pages",
                    where           = ("id",page_id)
                )[0]
            page_id  = result["parent"]
            data.append(result["shortcut"])

        # Liste umdrehen
        data.reverse()

        #~ data = [urllib.quote_plus(i) for i in data]

        link = "/".join(data)
        link = self.URLs.pageLink(link)
        return link

    #_________________________________________________________________________
    ## Funktionen für das ändern der Seiten

    def delete_page(self, page_id_to_del):
        first_page_id = self.get_first_page_id()
        if page_id_to_del == first_page_id:
            raise IndexError("The last page cannot be deleted!")

        self.delete(
            table = "pages",
            where = ("id",page_id_to_del),
            limit=1
        )

    def getUniqueShortcut(self, page_name, page_id = None):
        """
        Bearbeitet den gegebenen page_name so, das er Einmalig und "url-safe"
        ist.
        Ist eine page_id angegeben, wird der shortcut von dieser Seite
        ignoriert (wird beim edit page/preview benötigt!)
        """
        shortcutList = self.get_shortcutList(page_id)

        uniqueShortcut = self.tools.getUniqueShortcut(page_name, shortcutList)

        return uniqueShortcut

    #_________________________________________________________________________
    ## Funktionen für das ändern des Looks (Styles, Templates usw.)

    def update_style(self, style_id, style_data):
        lastupdatetime = self.tools.convert_time_to_sql(time.time())
        style_data["lastupdatetime"] = lastupdatetime
        try:
            style_data["lastupdateby"] = self.session['user_id']
        except AttributeError:
            # Wärend der installation gibt es kein session-Objekt!
            #~ style_data["lastupdateby"] = 0
            pass

        self.update(
            table   = "styles",
            data    = style_data,
            where   = ("id",style_id),
            limit   = 1
        )

    def new_style(self, style_data):
        self.insert(
            table   = "styles",
            data    = {
                "name"          : style_data["name"],
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
            table           = "styles",
            where           = ("plugin_id",plugin_id),
            limit           = 99,
        )
        style_names = [i["name"] for i in style_names]
        return style_names

    def update_template(self, template_id, template_data):
        self.update(
            table   = "templates",
            data    = template_data,
            where   = ("id",template_id),
            limit   = 1
        )

    def new_template(self, template_data):
        self.insert(
            table   = "templates",
            data    = template_data,
        )

    def delete_template(self, template_id):
        self.delete(
            table   = "templates",
            where   = ("id",template_id),
            limit   = 1
        )

    def change_page_position(self, page_id, position):
        self.update(
            table   = "pages",
            data    = {"position":position},
            where   = ("id",page_id),
            limit   = 1
        )

    #_________________________________________________________________________
    ## InterneSeiten

    def update_internal_page(self, internal_page_name, page_data):

        self.update(
            table   = "pages_internal",
            data    = page_data,
            where   = ("name",internal_page_name),
            limit   = 1
        )

    def new_internal_page(self, data, lastupdatetime=None):
        """
        Erstellt eine neue interne Seite.
        (installation!)
        """

        markup_id = self.get_markup_id(data["markup"])

        template_engine_id = self.get_template_engine_id(data["template_engine"])

        #~ self.page_msg(
            #~ "new internal page '%s': markup_id: %s, \
            #~ category_id: %s, template_engine_id: %s" % (
                #~ data["name"], markup_id, category_id, template_engine_id
            #~ )
        #~ )

        self.insert(
            table = "pages_internal",
            data  = {
                "name"              : data["name"],
                "plugin_id"         : data["plugin_id"],
                "method_id"         : data["method_id"],
                "template_engine"   : template_engine_id,
                "markup"            : markup_id,
                "lastupdatetime"    : self.tools.convert_time_to_sql(lastupdatetime),
                "content_html"      : data["content_html"],
                "content_css"       : data["content_css"],
                "content_js"        : data["content_js"],
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
            table           = "pages_internal",
            where           = ("plugin_id", plugin_id),
            limit           = 99,
        )
        page_names = [i["name"] for i in page_names]
        return page_names

    #_________________________________________________________________________
    ## Userverwaltung

    def add_md5_User(self, name, realname, email, pass1, pass2, admin):
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

    def update_userdata(self, id, name, realname, email, admin):
        """ Editierte Userdaten wieder speichern """
        user_data={
            "name": name, "realname": realname, "email": email, "admin": admin
        }

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

    #_________________________________________________________________________
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

    def install_plugin(self, module_data):
        """
        Installiert ein neues Plugin/Modul.
        Wichtig: Es wird extra jeder Wert herraus gepickt, weil in module_data
            mehr Keys sind, als in diese Tabelle gehören!!!
        """
        active = module_data["active"]
        if module_data.has_key("essential_buildin") and \
                                    module_data["essential_buildin"] == True:
            active = -1
        elif active == True:
            active = 1
        else:
            active = 0

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

        self.insert("plugins", data)
        return self.cursor.lastrowid

    def register_plugin_method(self, plugin_id, method_name, method_cfg):

        where= [("plugin_id", plugin_id), ("method_name", method_name)]

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

        # Daten vervollständigen
        method_cfg.update({
            "plugin_id"     : plugin_id,
            "method_name"   : method_name,
        })

        self.insert(
            table = "plugindata",
            data  = method_cfg,
        )
        return self.cursor.lastrowid

    def delete_plugin(self, id):
        try:
            self.delete(
                table = "plugins",
                where = ("id", id),
                limit = 999,
            )
        except Exception, e:
            raise IntegrityError(
                    "Can't delete plugin! ID: %s (%s: %s)" % (
                    id, sys.exc_info()[0],":", e
                )
            )

    def delete_plugindata(self, plugin_id):
        """
        Löscht alle Methoden zu einem Plugin
        """
        self.delete(
            table = "plugindata",
            where = ("plugin_id", plugin_id),
            limit = 999,
        )

    def delete_plugindata(self, plugin_id):
        """
        Löscht alle Methoden zu einem Plugin
        """
        self.delete(
            table = "plugindata",
            where = ("plugin_id", plugin_id),
            limit = 999,
        )

