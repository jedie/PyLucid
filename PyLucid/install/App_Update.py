#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

__history__="""
v0.2
    - update db tables (PyLucid v0.7.0 -> 0.7.1)
v0.1
    - erste Version
"""

import cgi, time

from PyLucid.install.ObjectApp_Base import ObjectApp_Base





class update(ObjectApp_Base):
    "3. update"
    def update1_db(self):
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



    def update2_db(self):
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
        if not table_keys.has_key("shortcut"):
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
        if not table_keys.has_key("name"):
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





















