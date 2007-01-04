#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Update PyLucid

Last commit info:
----------------------------------
LastChangedDate: $LastChangedDate$
Revision.......: $Rev$
Author.........: $Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__ = "$Rev$"


import cgi, time

from PyLucid.install.ObjectApp_Base import ObjectApp_Base





class update(ObjectApp_Base):
    "3. update"
    def update3_db(self):
        "update db tables (PyLucid v0.7.1 -> 0.7.2)"
        self._write_info()

        if not self._confirm("update db tables ?"):
            # Abfrage wurde nicht bestätigt
            return

        self.response.write("<h3>(some errors are normal!!!)</h3>\n")


        #_____________________________________________________________________
        # md5users Tabelle
        self.response.write("<h4>Change md5users table:</h4>\n")
        SQLcommand = (
            "ALTER TABLE $$md5users"
            " DROP pass2;"
        )
        msg = "Drop colum 'pass2'."
        self._execute(msg,SQLcommand)

        SQLcommand = (
            "ALTER TABLE $$md5users"
            " ADD username_md5 VARCHAR(32) NOT NULL AFTER realname;"
        )
        msg = "Insert colum 'username_md5'."
        self._execute(msg,SQLcommand)

        SQLcommand = (
            "ALTER TABLE $$md5users"
            " CHANGE pass1 md5checksum VARCHAR(64) NOT NULL"
        )
        msg = "Change 'pass1' colum, rename it to 'md5checksum'."
        self._execute(msg,SQLcommand)

        SQLcommand = (
            "ALTER TABLE $$md5users"
            " ADD salt INTEGER NOT NULL AFTER md5checksum;"
        )
        msg = "Add 'salt' colum."
        self._execute(msg,SQLcommand)

        # Daten in md5users Tabelle updaten
        self.response.write("<h4>Update data in md5users table:</h4>\n")
        self.response.write("<pre>\n")
        user_list = self._db.userList("name")
        for id in user_list:
            username = user_list[id]["name"]
            self.response.write("update user '%s'\n" % username)
            self._db.change_username(username,username)
        self.response.write("</pre>\n")

        #_____________________________________________________________________
        # Neue object_cache Tabelle
        self._execute("drop if exist","DROP TABLE IF EXISTS $$object_cache;")
        SQLcommand = (
            "CREATE TABLE $$object_cache ("
            " id VARCHAR(40) NOT NULL,"
            " expiry_time INT(15) NOT NULL,"
            " request_ip VARCHAR(15) DEFAULT NULL,"
            " user_id INT(11) DEFAULT NULL,"
            " pickled_data LONGBLOB,"
            " PRIMARY KEY (id)"
            ' ) COMMENT = "Object cache for pickled data objects";'
        )
        msg = "Create new object_cache table"
        self._execute(msg,SQLcommand)


        # Sessionhandling mit LONGBLOB
        self.response.write("<h4>Change Sessionhandling table:</h4>\n")
        SQLcommand = (
            "ALTER TABLE $$session_data"
            " CHANGE session_data session_data LONGBLOB NOT NULL;"
        )
        msg = "change column 'session_data' to a LONGBLOB value"
        self._execute(msg,SQLcommand)

        #_____________________________________________________________________
        # Neue plugin_cfg Spalte
        self._execute(
            "drop plugin_cfg, if exist","DROP TABLE IF EXISTS $$plugin_cfg;"
        )
        SQLcommand = (
            "ALTER TABLE $$plugins"
            " ADD COLUMN plugin_cfg LONGBLOB NOT NULL"
            " COMMENT 'pickled Python object structure'"
            " AFTER SQL_deinstall_commands"
        )
        msg = "Insert plugin_cfg column in 'plugins' table"
        self._execute(msg,SQLcommand)


    def update2_db(self):
        "update db tables (PyLucid v0.7.0 -> 0.7.1)"
        self._write_info()

        if not self._confirm("update db tables ?"):
            # Abfrage wurde nicht bestätigt
            return

        self.response.write("<h3>(some errors are normal!!!)</h3>\n")

        self.response.write("<h4>Delete obsolete TAL entry:</h4>\n")
        self.response.write("<pre>\n")
        try:
            self._db.delete(
                table = "template_engines",
                where = ("name","TAL"),
                limit = 1,
                debug = False
            )
        except Exception, e:
            self.response.write("ERROR: %s" % e)
        else:
            self.response.write("OK")
        self.response.write("</pre>\n")

        self._execute(
            title = "add 'lastupdateby' column in templates table",
            SQLcommand = (
                "ALTER TABLE $$templates ADD lastupdateby"
                " int(11) NOT NULL default '0' AFTER name;"
            )
        )

        # lastupdatetime einfügen
        for table in ("groups", "md5users", "templates", "user_group"):
            SQLcommand = (
                "ALTER TABLE $$%s ADD lastupdatetime"
                " datetime NOT NULL default '0000-00-00 00:00:00';"
            ) % table
            msg = (
                "add 'lastupdatetime' column in '%s'-table"
            ) % table
            self._execute(msg,SQLcommand)

        # lastupdateby einfügen
        for table in ("groups", "md5users", "templates", "user_group"):
            SQLcommand = (
                "ALTER TABLE $$%s ADD lastupdateby"
                " int(11) default NULL;"
            ) % table
            msg = (
                "add 'lastupdatetime' column in '%s'-table"
            ) % table
            self._execute(msg,SQLcommand)

        # createtime einfügen
        tables = (
            "md5users", "pages_internal", "groups", "templates", "user_group"
        )
        for table in tables:
            SQLcommand = (
                "ALTER TABLE $$%s ADD createtime"
                " datetime NOT NULL default '0000-00-00 00:00:00';"
            ) % table
            msg = (
                "add 'createtime' column in '%s'-table"
            ) % table
            self._execute(msg,SQLcommand)

        # datetime nach createtime umbenennen
        for table in ("pages", "styles", "templates", "pages_internal"):
            SQLcommand = (
                "ALTER TABLE $$%s"
                " CHANGE datetime createtime"
                " datetime NOT NULL default '0000-00-00 00:00:00';"
            ) % table
            msg = (
                "change column name 'datetime' to 'createtime' in '%s'-table"
            ) % table
            self._execute(msg,SQLcommand)



    def update1_db(self):
        "update db tables (PyLucid v0.6.x -> 0.7)"
        self._write_info()

        if not self._confirm("update db tables ?"):
            # Abfrage wurde nicht bestätigt
            return

        # page_internals
        SQLcommand = "DROP TABLE $$pages_internal_category;"
        self._execute(
            "Delete obsolete 'pages_internal_category' table", SQLcommand
        )
        SQLcommand = (
            "ALTER TABLE $$pages_internal"
            " DROP category_id;"
        )
        self._execute(
            "delete 'category_id' column in pages_internal table", SQLcommand
        )
        SQLcommand = (
            "ALTER TABLE $$pages_internal"
            " ADD method_id TINYINT(4) UNSIGNED NOT NULL AFTER plugin_id;"
        )
        self._execute(
            "add 'method_id' column in pages_internal table", SQLcommand
        )
        SQLcommand = (
            "ALTER TABLE $$pages_internal"
            " CHANGE plugin_id plugin_id TINYINT(4) UNSIGNED NOT NULL,"
            " CHANGE template_engine template_engine TINYINT(4) UNSIGNED NULL,"
            " CHANGE markup markup TINYINT(4) UNSIGNED NULL;"
        )
        self._execute(
            "change id columns in pages_internal table", SQLcommand
        )
        SQLcommand = (
            "ALTER TABLE $$pages_internal"
            " CHANGE content content_html TEXT NOT NULL;"
        )
        self._execute(
            "rename content to content_html in pages_internal table",
            SQLcommand
        )
        SQLcommand = (
            "ALTER TABLE $$pages_internal"
            " ADD content_css TEXT NOT NULL AFTER content_html;"
        )
        self._execute(
            "add 'content_css' column in pages_internal table", SQLcommand
        )
        SQLcommand = (
            "ALTER TABLE $$pages_internal"
            " ADD content_js TEXT NOT NULL AFTER content_html;"
        )
        self._execute(
            "add 'content_js' column in pages_internal table", SQLcommand
        )

        # shortcut Spalte hinzufügen
        SQLcommand = (
            "ALTER TABLE $$pages"
            " ADD shortcut"
            " VARCHAR(50) NOT NULL"
            " AFTER name;"
        )
        self._execute("Add 'shortcut' to pages table", SQLcommand)

        # shortcut auf unique setzten, falls das nicht schon der Fall ist
        table_keys = self._db.get_table_keys("pages")
        if not "shortcut" in table_keys:
            SQLcommand = "ALTER TABLE $$pages ADD UNIQUE (shortcut)"
            self._execute(
                "set 'shortcut' in pages table to unique",
                SQLcommand
            )

        self._updateStyleTable()

        # plugindata Aufräumen
        SQLcommand = (
            "ALTER TABLE $$plugindata"
            " DROP internal_page_info,"
            " DROP parent_method_id,"
            " DROP CGI_laws,"
            " DROP get_CGI_data;"
        )
        self._execute(
            "Remove obsolete column in table plugindata",
            SQLcommand
        )

        # plugins anpassen
        SQLcommand = (
            "ALTER TABLE $$plugins"
            " CHANGE package_name package_name"
            " VARCHAR( 128 ) NOT NULL;"
        )
        self._execute(
            "change size of package_name column in plugins-table",
            SQLcommand
        )

        # Verbesserung in der Tabelle, weil die Namen eindeutig sein sollen!
        table_keys = self._db.get_table_keys("template_engines")
        if not "name" in table_keys:
            SQLcommand = "ALTER TABLE $$template_engines ADD UNIQUE (name)"
            self._execute(
                "set 'name' in template_engines table to unique",
                SQLcommand
            )

        # jinja eintragen
        self.response.write("<h4>insert 'jinja' template engine:</h4>\n")
        self.response.write("<pre>\n")
        try:
            self._db.insert(
                table = "template_engines",
                data  = {"name": "jinja"}
            )
        except Exception, e:
            self.response.write("ERROR: %s" % e)
        else:
            self.response.write("OK")
        self.response.write("</pre>\n")

        self._db.commit()

    def _updateStyleTable(self):
        "Stylesheet-Tabelle mit Datumsfeldern versehen (PyLucid v0.6.x -> 0.7)"
        SQLcommand = (
            "ALTER TABLE $$styles"
            " ADD datetime DATETIME NOT NULL AFTER id,"
            " ADD lastupdatetime DATETIME NOT NULL AFTER datetime,"
            " ADD lastupdateby INT(11) NOT NULL AFTER lastupdatetime;"
        )
        self._execute("Add date-fields to stylesheets table", SQLcommand)

        defaultTime = self._tools.convert_time_to_sql(time.time())

        self.response.write("<h4>Update timestamps:</h4>")
        self.response.write("<pre>")
        styleList = self._db.get_style_list(["id","name"])
        for style in styleList:
            styleId = style["id"]
            styleName = style["name"]
            self.response.write(
                "update timestamp for '<strong>%s</strong>' ID:%s..." % (
                    styleName, styleId
                )
            )
            data = {
                "datetime": defaultTime,
                "lastupdatetime": defaultTime,
            }
            try:
                self._db.update_style(styleId, data)
            except Exception, e:
                self.response.write("Error: %s\n" % e)
            else:
                self.response.write("OK\n")

        self.response.write("</pre>")





















