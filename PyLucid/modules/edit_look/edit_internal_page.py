#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Editieren der internen Seiten.

Ausgelagerter Teil von edit_look.
"""

__history__ = """
v0.2
    - Neu: downloaden als ZIP
    - Neu: speichern in lokalen Dateien
v0.1
    - ausgelagert von edit_look.py
"""

import os, cgi, time, stat

from PyLucid.modules.edit_look.edit_look import __version__

from PyLucid.system.BaseModule import PyLucidBaseModule


class EditInternalPage(PyLucidBaseModule):

    content_types = {
        'content_html'  : "html",
        'content_css'   : "css",
        'content_js'    : "js",
    }

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

        # Den ID Benzug auflösen und Daten zusammenführen
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

            filename = "%s.zip" % data["name"]
            data["filename"] = filename
            data["url"] = self.URLs.actionLink(
                "download_internal_page", filename, addSlash=False
            )
            data["diff_url"] = self.URLs.actionLink(
                "internal_page_diff", data["name"]
            )

            contextDict[package_name][module_name].append(data)

        # Baut eine Liste fÃ¼r jinja zusammen
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

        all_filename = self.download_all_filename()
        changed_filename = self.download_changed_filename()

        context = {
            "itemsList": context_list,
            #~ "url": self.URLs.currentAction(),
            "url": self.URLs.actionLink("edit_internal_page"),
            "download_all": self.URLs.actionLink(
                "download_internal_page", all_filename, addSlash=False
            ),
            "download_changed": self.URLs.actionLink(
                "download_internal_page", changed_filename, addSlash=False
            ),
            "save_all_local": self.URLs.actionLink("save_all_local"),
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

        markups = self.db.get_available_markups()
        current_markup = edit_data["markup"]

        engines = self.db.get_available_template_engines()
        current_engine = edit_data["template_engine"]

        context = {
            "name"          : internal_page_name,
            "back_url"      : self.URLs.actionLink("internal_page"),
            "url"           : self.URLs.actionLink("internal_page"),
            "list_url"      : self.URLs.commandLink("pageadmin", "tag_list"),
            "content_html"  : cgi.escape(edit_data["content_html"]),
            "content_css"   : cgi.escape(edit_data["content_css"]),
            "content_js"    : cgi.escape(edit_data["content_js"]),
            "description"       : cgi.escape(edit_data["description"]),
            "markups"           : markups,
            "current_markup"    : current_markup,
            "engines"         : engines,
            "current_engine"  : current_engine,
        }
        #~ self.page_msg(context)
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

        # interne Seite abspeichern
        page_data = {
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
    ## Download der internen Seiten

    def _gettime(self):
        return time.strftime("%Y%m%d", time.localtime())

    def download_all_filename(self):
        return "%s_PyLucid_internalpages_all.zip" % self._gettime()
    def download_changed_filename(self):
        return "%s_PyLucid_internalpages_changed.zip" % self._gettime()


    def download_internal_page(self, function_info):
        """
        Download der internen Seiten als ZIP
        """
        download_filename = function_info[0]

        def upload(download_filename, zipfile):
            zipfile.debug(self.page_msg)

            self.response.startFileResponse(
                download_filename, zipfile.get_len()
            )
            zipfile.block_write(out_object = self.response)
            return self.response

        if download_filename.endswith(self.download_all_filename()):
            # Download aller internen Seiten
            self.response.write("Download all")
            internalpage_data = self.get_all_internalpage_data()
            zipfile = self.make_archive(internalpage_data)

            #~ self.response.startFileResponse(
                #~ download_filename, zipfile.get_len()
            #~ )
            #~ zipfile.block_write(out_object = self.response)
            #~ return self.response
            return upload(download_filename, zipfile)

        elif download_filename.endswith(self.download_changed_filename()):
            # Nur die geänderten internen Seiten downloaden
            self.response.write("Download the newest")

        else:
            try:
                zipfile = self.download_one(download_filename)
            except WrongInternalPagename, e:
                self.page_msg(e)
                self.internal_page() # Auswahl wieder anzeigen lassen
                return
            return upload(download_filename, zipfile)

        self.response.write("<p>Not available yet :(</p>")

    def download_one(self, internal_page_name):
        """
        Download einer bestimmten internen Seite
        """
        internal_page_name, ext = os.path.splitext(internal_page_name)
        try:
            # Daten der internen Seite, die editiert werden soll
            internalpage_data = self.db.get_internal_page_data(
                internal_page_name
            )
        except IndexError:
            msg = (
                "bad internal-page name: '%s' !"
            ) % cgi.escape(internal_page_name)
            raise WrongInternalPagename(msg)

        self.page_msg(internalpage_data)

        zipper = self.tools.StringIOzipper(self.page_msg)

        for content_type, ext in self.content_types.iteritems():
            content = internalpage_data[content_type]
            if not content:
                # Kein CSS oder JS da
                continue

            arcname = "%s.%s" % (internal_page_name, ext)
            zipper.add_file(arcname, content)

        zipper.close()
        return zipper

    def get_all_internalpage_data(self):

        package_names = self.db.pluginsList(select_items=["package_name"])
        #~ self.page_msg(package_names)

        internal_pages = self.db.internalPageList(
            select_items=["name", "plugin_id", 'lastupdatetime']
        )
        #~ self.page_msg(internal_pages)

        for internal_page, data in internal_pages.iteritems():
            plugin_id = data['plugin_id']
            package_name = package_names[plugin_id]['package_name']
            data['package_name'] = package_name
            data['dir_list'] = package_name.split(".")
            data['path'] = os.path.join(*data['dir_list'])

            #~ self.page_msg(data)

        #~ self.page_msg(internal_pages)
        return internal_pages

    def make_archive(self, internalpage_data):

        zipper = self.tools.StringIOzipper(self.page_msg)

        internalpage_data = self.get_all_internalpage_data()
        #~ self.page_msg(internalpage_data)
        dircache = {}
        for name, data in internalpage_data.iteritems():
            #~ self.page_msg(name)
            #~ self.page_msg(data)

            internalpage_data = self.db.get_internal_page_data(name)
            #~ self.page_msg(internalpage_data)

            for content_type, ext in self.content_types.iteritems():
                content = internalpage_data[content_type]
                if not content:
                    # Kein CSS oder JS da
                    continue

                filename = "%s.%s" % (name, ext)
                arcname = os.path.join(data["path"], filename)

                #~ self.page_msg(len(content), filename, arcname)

                zipper.add_file(arcname, content)

        zipper.close()
        return zipper


    #_______________________________________________________________________

    def save_all_local(self):
        """
{u'PageUpdateTable': {'content_css': u'#page_updates tr:hover {   /* Maus \ufffdem Link */\r\n\tcolor: #000;\r\n\ttext-decoration:underline;\r\n\tbackground-color: #eee;\r\n}',
                      'content_html': u'<table id="page_updates">\r\n  <tr>\r\n    <th>update time</th>\r\n    <th>page</th>\r\n    <th>update by</th>\r\n  </tr>\r\n{% for item in page_updates %}\r\n  <tr>\r\n    <td>{{ item.date }}</td>\r\n    <td><a href="{{ item.link }}">{{ item.name_title|escapexml }}</td>\r\n    <td>{{ item.user }}</td>\r\n  </tr>\r\n{% endfor %}\r\n</table>',
                      'content_js': u'',
                      'description': u'Table for the list of page updates',
                      'lastupdateby': 1L,
                      'lastupdatetime': datetime.datetime(2006, 8, 30, 9, 35, 53),
                      'markup': 1,
                      'method_id': 21,
                      'name': u'PageUpdateTable',
                      'plugin_id': 4,
                      'template_engine': 4},
"""

        # Zähler für die Anzahl der lokal aktualisierten Dateien
        self.updated_files = 0

        backlink = (
            '<a href="%s">back</a>\n'
        ) % self.URLs.actionLink("internal_page")

        self.response.write("<h2>detail</h2>\n")
        self.response.write(backlink)

        internalpage_data = self.get_all_internalpage_data()
        #~ self.page_msg(internalpage_data)
        dircache = {}
        for name, data in internalpage_data.iteritems():
            internalpage_data = self.db.get_internal_page_data(name)

            #~ self.page_msg(name)
            #~ self.page_msg(data)
            #~ self.page_msg(internalpage_data)

            self.response.write("<h3>%s</h3>\n" % name)
            self.response.write("<pre>\n")

            self.updatefile(
                "html", internalpage_data['content_html'], data
            )
            self.updatefile(
                "css", internalpage_data['content_css'], data
            )
            self.updatefile(
                "js", internalpage_data['content_js'], data
            )
            self.response.write("</pre>\n")

            #Aus dem Packages nur Dateien, der aktuellen internen Seite filtern
            #~ filelist = filefilter(filelist, name)

        self.page_msg("%s files updated" % self.updated_files)
        self.response.write(backlink)


    def updatefile(self, typ, content, internalpage_data):
        """
        Updated die lokale Datei für einen Typ (html, css oder js)
        """
        dir = os.path.join(*internalpage_data['dir_list'])
        filename = "%s.%s" % (internalpage_data['name'], typ)
        filepath = os.path.join(dir, filename)

        if content == "":
            # Keine Daten zum aktuellen Typ
            if not os.path.isfile(filepath):
                # Ist auch keine Datei vorhanden
                return

            # vorhandene Datei löschen
            try:
                os.remove(filepath)
            except Exception, e:
                self.page_msg(
                    "Can't delete obsolete file '%s': %s" % (filepath, e)
                )
            return

        self.response.write("%s\n" % filepath)

        #~ self.writefile(filepath, content)
        #~ return

        if not os.path.isfile(filepath):
            self.response.write("\tfile does not exist!\n")
            self.writefile(filepath, content)
            return

        # Datei existiert auf Platte

        file_mtime = os.stat(filepath)[stat.ST_MTIME]
        lastupdatetime = internalpage_data['lastupdatetime']
        # datetime in time-epoche-sec wandeln
        db_mtime = time.mktime(lastupdatetime.timetuple())

        if file_mtime<db_mtime:
            # Datei ist älter als DB daten -> Updaten
            self.writefile(filepath, content)
            return

        # lokale Datei ist neuer
        self.response.write(
            '\t<strong>File date is newer!!!</strong>\n'
        )

        self.response.write(
            "\tfiledate: %s - db-date: %s\n" % (
                self.tools.strftime(file_mtime),
                self.tools.strftime(db_mtime)
            )
        )
        self.display_diff(filepath, content)
        self.response.write("\n\n")
        return


    def writefile(self, filepath, content):
        """
        content in Datei schreiben
        """
        try:
            content = content.encode("UTF8", "strict")
        except UnicodeError, e:
            self.page_msg("UnicodeError: %s" % e)
            self.page_msg("(Use 'replace' Errorhandling!)")
            content = content.encode("UTF8", "replace")

        content = content.replace("\r\n", "\n").replace("\r", "\n")

        try:
            f = file(filepath, "wb")
            f.write(content)
            f.close()
        except Exception, e:
            self.page_msg("Can't write file '%s': %s" % (filepath, e))
        else:
            msg = "\tLocal file '%s' updated successful.\n" % filepath
            self.response.write(msg)
            self.page_msg(msg)
            self.updated_files += 1

        self.response.write("\n")


    def display_diff(self, filepath, content):
        f = file(filepath, "rU")
        file_content = f.readlines()
        f.close()

        db_content = content.splitlines()

        #~ file_content = [i.decode("utf8") for i in file_content]
        db_content = [i.encode("utf8") for i in db_content]

        import difflib

        #~ nd = difflib.ndiff(file_content, db_content)

        d = difflib.HtmlDiff()
        diff_table = d.make_table(
            file_content, db_content,
            filepath.encode("UTF8"), "db",
            context=True
        )
        # FIXME: Quick and dirty hack:
        if "No Differences Found" in diff_table:
            # Keine Änderungen gefunden
            self.response.write("No differences.")
            return

        # Oder nur als HTML Tabelle
        # CSS Klassen sind zwar auch hier schon vorgegeben, lassen sich aber
        # durch eigene CSS angaben ändern. (Ist auch nötig)
        self.response.write(diff_table)
        return


        #~ d = difflib.Differ()

        #~ self.response.write("<pre>")

        #~ line = 0
        #~ sep_printed = False
        #~ for i in d.compare(file_content, db_content):
            #~ line += 1
            #~ if i[0] in ("+","-","?"): # Geänderte Zeile
                #~ sep_printed = False
                #~ i = i.rstrip("\n")
                #~ self.response.write("%5s %s\n" % (line, cgi.escape(i)))
                #~ oldline = line
            #~ else:
                #~ if sep_printed==False:
                    #~ sep_printed = True
                    #~ self.response.write("-"*79)
                    #~ self.response.write("\n")

        #~ self.response.write("</pre>")


    #_______________________________________________________________________

    def internal_page_diff(self, function_info):
        """
        Diff Anzeigen
        """
        internal_page_name = function_info[0]

        backlink = (
            '<p><a href="%s">back</a></p>\n'
        ) % self.URLs.actionLink("internal_page")

        self.response.write(
            "<h2>diff between db content and local file content</h2>\n"
        )
        self.response.write(backlink)

        # name, createtime, plugin_id, method_id, template_engine, markup,
        # lastupdatetime, lastupdateby, content_html, content_js, content_css,
        # description
        select_items = [
            "plugin_id", "content_html", "content_css", "content_js",
            "description", "lastupdatetime", "lastupdateby",
        ]

        try:
            # Daten der internen Seite, die editiert werden soll
            internalpage_data = self.db.get_internal_page_data(
                internal_page_name, select_items=select_items, replace=False
            )
        except IndexError:
            msg = (
                "bad internal-page name: '%s' !"
            ) % cgi.escape(internal_page_name)
            raise WrongInternalPagename(msg)

        #~ self.page_msg(internalpage_data)

        plugin_id = internalpage_data['plugin_id']
        plugin_data = self.db.get_plugin_data_by_id(
            plugin_id, select_items = 'package_name'
        )
        #~ self.page_msg(plugin_data)

        package_name = plugin_data["package_name"]
        dir_list = package_name.split(".")
        dir = os.path.join(*dir_list)

        for content_type, ext in self.content_types.iteritems():
            db_content = internalpage_data[content_type]
            if not db_content:
                # Kein CSS oder JS da
                continue

            filename = "%s.%s" % (internal_page_name, ext)
            filepath = os.path.join(dir, filename)

            self.response.write("<h3>%s</h3>\n" % filepath)
            self.display_diff(filepath, db_content)

        self.response.write(backlink)

    #_______________________________________________________________________
    ## Allgemeine Funktionen

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





class WrongInternalPagename(Exception):
    """
    Beim Download wurde ein falscher Name angegeben
    """
    pass