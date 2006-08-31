#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

import cgi


from PyLucid.system.exceptions import *


from PyLucid.install.ObjectApp_Base import ObjectApp_Base
from PyLucid.install.SQLdump import SQLdump



table_rename_form = """
<p>Here you can rename the prefix of all current PyLucid tables.<br />
The current used prefix is: <strong>"%(prefix)s"</strong></p>
<p><strong>Note:</strong></p>
<ul>
    <li>The new prefix shoudn't contain blanks!</li>
    <li>You must manually update the config.py!</li>
</ul>

<fieldset><legend>rename form</legend>
    <form name="confirm" method="post" action="%(url)s">
        <label for="new_name">new table prefix:</label>
        <input id="new_prefix" name="new_prefix"
            type="text" value="" size="20" maxlength="20" />
        <br />
        <label for="simulation">Simulation only:</label>
        <input id="simulation" name="simulation"
            type="checkbox" value="True" checked="checked" />
        <br />
        <input type="submit" value="rename" name="rename" />
    </form>
</fieldset>
"""







class LowLevelAdmin(ObjectApp_Base):
    "2. low level Admin"
    def rebuildShortcuts(self):
        "Rebuild all shortcuts"
        self._write_info()

        self.response.write("<h4>Create shortcut's from pages names:</h4>\n")
        self.response.write("<pre>\n")
        result = self._db.select(
            select_items    = ["id","name","title"],
            from_table      = "pages",
        )
        nameList = []
        for line in result:
            id = line["id"]
            name = line["name"]
            if name=="" or name==None:
                name = line["title"]

            self.response.write("id %-3s: %-30s -&gt;" % (id,cgi.escape(name)))

            shortcut = self._tools.getUniqueShortcut(name, nameList)
            nameList.append(shortcut)

            self.response.write("%-30s" % shortcut)

            self.response.write("--- update in db:")

            try:
                self._db.update(
                    table   = "pages",
                    data    = {"shortcut": shortcut},
                    where   = ("id",id)
                )
            except Exception, e:
                self.response.write("ERROR: %s" % e)
            else:
                self.response.write("OK")

            self.response.write("\n")
        self.response.write("</pre>\n")

    #_________________________________________________________________________

    def module_admin(self):
        "Module/Plugin Administration"
        #~ self._write_info()
        self._write_backlink()

        module_admin = self._get_module_admin()

        #~ self.response.debug()
        #~ return

        module_admin.menu()

    #_________________________________________________________________________

    def re_init(self):
        "partially re-initialisation DB tables"
        self._write_info()

        simulation = self.request.form.get("simulation",False)
        d = SQLdump(self.request, self.response, simulation)

        selectedTables = self.request.form.getlist("tablename")
        if selectedTables!=[]:
            # Forumlar wurde abgeschickt
            d.install_tables(selectedTables)
            return

        txt = (
            '<form action="%s" method="post">\n'
            '<p>Which tables reset to defaults:</p>\n'
        ) % self._URLs.currentAction()
        self.response.write(txt)

        for name in d.get_table_names():
            txt = (
                '<input type="checkbox" id="%(name)s" name="tablename" value="%(name)s">'
                '<label for="%(name)s">%(name)s</label><br />\n'
            ) % {"name": name}
            self.response.write(txt)

        self.response.write(
            '<h4><strong>WARNING:</strong> The specified tables lost all Data!</h4>\n'
            '<label for="simulation">Simulation only:</label>\n'
            '<input id="simulation" name="simulation"'
            ' type="checkbox" value="yes" checked="checked" />\n'
            '<br />\n'
            '<input type="submit" value="reinit" name="reinit" />\n'
            '</form>\n'
        )

    #_________________________________________________________________________

    def repair_auto_increment(self):
        "repair 'auto increment'"
        self._write_info()

        self.response.write(
            "<small>(only tables with prefix '%s')</small>" % \
                                                    self._db.tableprefix
        )
        self.response.write("<ul>")
        tableNameList = self._db.get_tables()
        for tableName in tableNameList:
            self.response.write('<li>%s<br />' % tableName)

            SQLcommand = "SHOW COLUMNS FROM %s LIKE 'id';" % tableName
            try:
                self._db.cursor.execute(SQLcommand)
            except Exception, e:
                self.response.write("execude ERROR: %s\n" % e)
                self.response.write("SQLcommand: %s\n" % SQLcommand)
                self.response.write("</li>\n")
                continue

            result = self._db.cursor.fetchone()
            if result == () or result["Extra"] == "auto_increment":
                # Hat kein "id" Spalte oder "auto_increment" ist gesetzt.
                self.response.write("OK")
            else:
                # Muß gesetzt werden
                self.response.write("%s<br />" % result)
                SQLcommand = (
                    "ALTER TABLE %(table_name)s CHANGE %(field)s"
                    " %(field)s %(type)s AUTO_INCREMENT;"
                ) % {
                    "table_name": tableName,
                    "field": result["Field"], # 'id'
                    "type": result["Type"],
                }
                self.response.write("%s<br />" % SQLcommand)
                try:
                    self._db.cursor.execute(SQLcommand)
                except Exception, e:
                    self.response.write("execude ERROR: %s\n" % e)
                    self.response.write("SQLcommand: %s\n" % SQLcommand)
                    self.response.write("</li>\n")
                    continue
                else:
                    self.response.write("fixed!")

            self.response.write("</li>\n")

        self.response.write("</ul>")

        self._db.commit()

    #_________________________________________________________________________

    def rename_tables(self):
        "rename all tables"
        self._write_info()
        #~ self.response.debug()

        tableNameList = self._db.get_tables()
        if len(tableNameList)==0:
            msg = (
                '<p>There are no tables with the current prefix'
                ' <strong>"%s"</strong>!</p>'
                '<p><small>'
                'You must update config.py or you use "init Database tables"'
                ' to create a new installation.'
                '</small></p>'
            ) % self._db.tableprefix
            self.response.write(msg)
            return

        if not "new_prefix" in self.request.form:
            form = table_rename_form % {
                "prefix": self._db.tableprefix,
                "url"   : self._URLs.currentAction()
            }
            self.response.write(form)
            return

        if "simulation" in self.request.form:
            simulation = True
        else:
            simulation = False

        new_prefix = self.request.form["new_prefix"]

        # Leerzeichen vorsichtshalber entfernen ;)
        new_prefix = new_prefix.replace(" ","")

        self.response.write("<pre>")

        for tableName in tableNameList:
            self.response.write('%-30s' % tableName)

            self.response.write('--&gt;&gt; ')

            new_name = tableName.replace(self._db.tableprefix, new_prefix)

            self.response.write('%-30s' % new_name)

            SQLcommand = "RENAME TABLE %s TO %s" % (tableName, new_name)

            if simulation:
                self.response.write("\n&gt;&gt;&gt; %s\n\n" % SQLcommand)
                continue

            try:
                self._db.cursor.execute(SQLcommand)
            except Exception, e:
                self.response.write("execude ERROR: %s\n" % e)
                self.response.write("SQLcommand: %s\n" % SQLcommand)
            else:
                self.response.write("OK\n")

        self.response.write("</pre>")






