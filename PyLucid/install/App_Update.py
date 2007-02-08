#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Update PyLucid

Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

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
    def update2_db(self):
        "update db tables (PyLucid v0.7.1 -> 0.7.2)"
        self._write_info()

        if not self._confirm("update db tables ?"):
            # Abfrage wurde nicht bestätigt
            return

        self.response.write("<h3>(some errors are normal!!!)</h3>\n")


        #_____________________________________________________________________
        # Preferences

        self.response.write("<h4>Change preferences:</h4>\n")
        try:
            self._preferences.change(
                section="core", varName="defaultPageName",
                change_dict = {
                    "varName": "defaultPage",
                    "description": (
                        'This is the default page that a site visitor will see'
                        ' if they arrive at your CMS without specifying a'
                        ' particular page.'
                    )
                }
            )
        except Exception, e:
            self.response.write("Error: %s (Already changed?)" % e)
        else:
            self.response.write("defaultPageName renamed to defaultPage, OK")

        #_____________________________________________________________________

        self._execute(
            "drop appconfig if exist","DROP TABLE IF EXISTS $$appconfig;"
        )

        #_____________________________________________________________________
        # md5users Tabelle
        self.response.write("<h4>Change md5users table:</h4>\n")
        SQLcommand = (
            "ALTER TABLE $$md5users"
            " DROP pass2;"
        )
        msg = "Drop colum 'pass2'."
        self._execute(msg,SQLcommand)

        SQLcommand = "ALTER TABLE $$md5users DROP COLUMN username_md5;"
        msg = "Drop colum 'username_md5'."
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

        # Hatte sich mal in die Install-Daten eingeschlichen :(
        self._execute(
            "drop md5users2 if exist","DROP TABLE IF EXISTS $$md5users2;"
        )

        #_____________________________________________________________________
        # Neue l10n Tabelle
        self._execute("drop if exist","DROP TABLE IF EXISTS $$l10n;")
        SQLcommand = (
            "CREATE TABLE $$l10n ("
            " id INT NOT NULL AUTO_INCREMENT,"
            " lang VARCHAR(2) NOT NULL DEFAULT '',"
            " varName VARCHAR(50) NOT NULL DEFAULT '',"
            " value VARCHAR(255) NOT NULL DEFAULT '',"
            " description VARCHAR(255) NOT NULL DEFAULT '',"
            " PRIMARY KEY(id)"
            ' ) COMMENT = "l10n data for any languages";'
        )
        msg = "Create new l10n table"
        self._execute(msg,SQLcommand)
        self._db.insert("l10n", {
            "lang":"en", "varName":"datetime", "value":'%Y-%m-%d - %H:%M',
            "description": "The Python Format for Date and Time value."
        })
        self._db.insert("l10n", {
            "lang":"de", "varName":"datetime", "value":'%d.%m.%Y - %H:%M',
            "description": "Datum und Uhrzeit im Python Format."
        })

        #_____________________________________________________________________
        # Neue object_cache Tabelle
        self._execute("drop if exist","DROP TABLE IF EXISTS $$object_cache;")
        SQLcommand = (
            "CREATE TABLE $$object_cache ("
            " id VARCHAR(40) NOT NULL,"
            " expiry_time INT(15) NOT NULL,"
            " request_ip VARCHAR(15) DEFAULT NULL,"
            " user_id INT(11) DEFAULT NULL,"
            " pickled_data TEXT,"
            " PRIMARY KEY (id)"
            ' ) COMMENT = "Object cache for pickled data objects";'
        )
        msg = "Create new object_cache table"
        self._execute(msg,SQLcommand)
        # Evtl. von einer Beta Version (alter LONGBLOB):
        SQLcommand = (
            "ALTER TABLE $$object_cache"
            " CHANGE pickled_data pickled_data TEXT NULL DEFAULT NULL "
            " COMMENT 'Object cache for pickled data objects'"
        )
        msg = "Insert plugin_cfg column in 'plugins' table"
        self._execute(msg,SQLcommand)

        # Sessionhandling mit TEXT
        self.response.write("<h4>Change Sessionhandling table:</h4>\n")
        SQLcommand = (
            "ALTER TABLE $$session_data"
            " CHANGE session_data session_data TEXT NOT NULL"
            " COMMENT 'pickled Python object structure';"
        )
        msg = "change column 'session_data' to a TEXT value"
        self._execute(msg,SQLcommand)

        #_____________________________________________________________________
        # Neue plugin_cfg Spalte
        self._execute(
            "drop plugin_cfg, if exist","DROP TABLE IF EXISTS $$plugin_cfg;"
        )
        SQLcommand = (
            "ALTER TABLE $$plugins"
            " ADD COLUMN plugin_cfg TEXT DEFAULT NULL"
            " COMMENT 'pickled Python object structure'"
            " AFTER SQL_deinstall_commands;"
        )
        msg = "Insert plugin_cfg column in 'plugins' table"
        self._execute(msg,SQLcommand)
        # Evtl. von einer Beta Version (alter LONGBLOB):
        SQLcommand = (
            "ALTER TABLE $$plugins"
            " CHANGE plugin_cfg plugin_cfg TEXT NULL DEFAULT NULL "
            " COMMENT 'pickled Python object structure'"
        )
        msg = "Insert plugin_cfg column in 'plugins' table"
        self._execute(msg,SQLcommand)


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


