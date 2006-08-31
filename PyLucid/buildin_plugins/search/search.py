#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einfache Suche in CMS Seiten
"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

__version__="0.4"

__history__="""
v0.4
    - Anpassung an colubrid 1.0
v0.3
    - Updates für die neue SQL- und URL-Klasse
v0.3
    - Nutzt nun self.db.print_internal_page()
    - Nutzt "get_CGI_data"
v0.2
    - Führt eine einfache Gewichtung der Ergebnisse durch, dabei werden die Meta-Daten
        der Seite herran gezogen.
v0.1
    - erste Version
"""

__todo__ = """
"""


import cgi, time, urllib

from PyLucid.system.BaseModule import PyLucidBaseModule

class search(PyLucidBaseModule):

    def lucidTag(self, search_string=""):
        search_string = cgi.escape(search_string).replace('"',"'")
        context = {
            "url"               : self.URLs.actionLink("do_search"),
            "old_search_string" : search_string
        }
        self.templates.write("input_form", context)

    def do_search(self):
        start_time = time.time()
        self.response.write(
            "<h2>search v%s</h2>" % __version__
        )

        self.print_last_search_words()

        search_string = self.request.form.get("search_string","")

        #~ self.debug()

        if search_string == "":
            # Evtl. in den GET durch den Link von einer alten Suche:
            search_string = self.request.args.get("search_string","")
            if search_string == "":
                self.page_msg("No search string found.")
                self.lucidTag()
                return

        search_words = self.filter_search_string(search_string)
        if not search_words:
            # Alle Wörter waren doof
            self.response.write(
                "<p>Sorry, no search Strings remaining</p>"
            )
            # Suchmaske anzeigen
            self.lucidTag()
            return

        result = self.search_in_DB(search_words)
        result_count = len(result)

        if result_count == 0:
            self.response.write(
                "<p>Sorry, nothing found. Try again:</p>"
            )
            self.log(search_string, "search", "False")
            # Such-Eingabemaske wieder anzeigen
            self.lucidTag(search_string)
            return

        self.log(
            "[%s] Count: %s" % (search_string,result_count), "search", "OK"
        )

        self.response.write(
            "<h3>%s results for '%s' (%0.2fsec.):</h3>" % (
                result_count, cgi.escape(" ".join(search_words)),
                time.time() - start_time
            )
        )
        self.display_results( result, search_words )

    def print_last_search_words( self ):
        """
        Ausgabe der letzten fünf Suchwörter
        """
        result = self.db.select(
            select_items    = ["message","domain"],
            from_table      = "log",
            where           = [("typ","search"),("status","OK")],
            order           = ("timestamp","DESC"),
            limit           = (0,5)
        )
        self.response.write("<h4>Last 5 search words:</h4>\n")
        self.response.write('<ol id="last_search_words">\n')
        for line in result:
            message = line["message"]

            # rsplit gibt's erst ab Python 2.4
            count = message.split(":")[-1]
            search_words = message.split("]")[0][1:]

            url = '%s?search_string=%s' % (
                self.URLs.commandLink("search", "do_search"),
                urllib.quote_plus(search_words)
            )

            self.response.write(
                '\t<li><a href="%s">%s</a>&nbsp;<small>(%s results, %s)</small></li>\n' % (
                    url, search_words, count, line["domain"]
                )
            )
        self.response.write("</ol>\n")

    def filter_search_string(self, RAW_search_string):
        """
        Filtert Suchbegriffe
            - zu kleine Wörter fallen raus
            - keine doppelten Wörter
        """
        min_len = 3
        search_string = []
        ignore = []
        for word in RAW_search_string.split(" "):
            if len(word)<=(min_len-1):
                # Zu kurzes Wort
                ignore.append(word)
            elif search_string.count(word) == 0: # Keine doppelten
                search_string.append(word)
        if ignore != []:
            self.response.write(
                "<p>Ignore: '%s' (too small, min len %s)</p>\n" % (
                    ",".join([cgi.escape(i) for i in ignore]), min_len
                )
            )
        return search_string

    def search_in_DB(self, search_words):
        """
        Eigentliche Suche in DB
        """
        partial_result = {}

        # UND suche im Text aller CMS Seiten
        result = self.db.process_statement(
            SQLcommand = "SELECT id,content FROM $$pages WHERE content LIKE %s",
            SQL_values = ( "%%%s%%" % "%".join(search_words), )
        )
        for line in result:
            id = line["id"]
            points = 0
            for word in search_words:
                points += line["content"].count(word)
            partial_result[id] = points

        # ODER suche in Meta-Daten
        for column in ("keywords","description","name","title"):
            where_string = " OR ".join(
                [column+" LIKE %s" for i in xrange(len(search_words))]
            )
            result = self.db.process_statement(
                SQLcommand = "SELECT id FROM $$pages WHERE %s" % where_string,
                SQL_values = tuple( ["%%%s%%" % i for i in search_words] )
            )
            for line in result:
                id = line["id"]
                if partial_result.has_key(id):
                    partial_result[id] *= 1.5
                else:
                    partial_result[id] = 1

        # Dict umkehren Key ist die Punkte-Zahl und value eine Liste mit den
        # IDs der Seiten, die die Punkte Zahl haben
        result_IDs = {}
        for id,points in partial_result.iteritems():
            if result_IDs.has_key(points):
                result_IDs[points].append(id)
            else:
                result_IDs[points] = [id]

        # Eine sortiere Liste alle Punkte in absteigender Reihenfolge erstellen
        point_list = result_IDs.keys()
        point_list.sort()
        point_list.reverse()

        # Daten zu den eigentlichen Ergebnissen für jede Seite aus der DB holen
        result = []
        for points in point_list:
            for id in result_IDs[points]:
                side_info = self.db.process_statement(
                    SQLcommand = (
                        "SELECT id,name,title,content"
                        " FROM $$pages WHERE id=%s"
                    ),
                    SQL_values = (id,)
                )[0]
                side_info["points"] = points # Punkte hinzufügen
                result.append( side_info )

        return result

    def display_results( self, result, search_words ):
        """
        Ergebnisse der Suche anzeigen
        """
        text_cut = 50
        self.response.write("<ol>\n")
        for hit in result:
            self.response.write("<li>\n")
            self.response.write('<p><a href="%s"><strong>%s</strong>\n' % (
                    self.db.get_page_link_by_id(hit["id"]),
                    cgi.escape(hit["name"])
                )
            )
            if (hit["title"] != "") and (hit["title"] != None) and hit["title"] != hit["name"]:
                self.response.write(" - %s" % cgi.escape(hit["title"]))

            self.response.write(
                "</a>&nbsp;<small>(%s points)</small>" % hit["points"]
            )
            self.response.write("<br />\n<small>\n")
            for s in search_words:
                content = cgi.escape(hit["content"])
                try:
                    index = content.index(s)
                except ValueError:
                    pass
                else:
                    txt = content[index-text_cut:index+text_cut]
                    txt = txt.replace(s,"<strong>%s</strong>" % s)
                    if txt == "": continue
                    self.response.write("...%s...<br />\n" % txt)
            self.response.write("</small>\n")

            self.response.write("</p></li>\n")
        self.response.write("</ol>\n")

