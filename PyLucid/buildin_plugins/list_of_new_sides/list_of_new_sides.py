#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:list_of_new_sides />
Generiert eine Liste der "letzten Änderungen"
"""

__version__="0.3"

__history__="""
v0.3
    - Erweitert: zeigt nun an, wer die Änderunen vorgenommen hat.
    - Nutzt ein jinja Template.
    - Zeigt nun immer die letzten 10 Änderungen, statt 5.
v0.2
    - Anpassung an v0.7
v0.1.1
    - Bugfix: URLs heißt das und nicht URL
v0.1.0
    - Anpassung an neuen Modul-Manager
v0.0.5
    - Anpassung an neuer Absolute-Seiten-Addressierung
v0.0.4
    - Bugfix: SQL Modul wird anders eingebunden
v0.0.3
    - Anpassung an index.py (Rendern der CMS-Seiten mit Python'CGIs)
    - SQL-Connection wird nun auch beendet
v0.0.2
    - Anpassung an neue SQL.py Version
    - Nur Seiten Anzeigen, die auch permitViewPublic=1 sind (also öffentlich)
v0.0.1
    - erste Version
"""




# Python-Basis Module einbinden
import cgi, re


from PyLucid.system.BaseModule import PyLucidBaseModule


class list_of_new_sides(PyLucidBaseModule):

    def lucidTag(self):
        """
        Aufruf über <lucidTag:list_of_new_sides />
        """
        SQLresult = self.db.select(
            select_items    = [
                "id", "name", "title", "lastupdatetime", "lastupdateby"
            ],
            from_table      = "pages",
            where           = ( "permitViewPublic", 1 ),
            order           = ( "lastupdatetime", "DESC" ),
            limit           = ( 0, 10 )
        )

        userlist = [item["lastupdateby"] for item in SQLresult]
        tmp = {}
        for user in userlist:
            tmp[user] = None
        userlist = tmp.keys()

        where = ["(id=%s)" for i in userlist]
        where = " or ".join(where)

        SQLcommand = "SELECT id,name FROM $$md5users WHERE %s" % where
        users = self.db.process_statement(SQLcommand, userlist)
        #~ self.page_msg(users)
        users = self.db.indexResult(users, "id")
        #~ self.page_msg(users)

        #~ self.page_msg(SQLresult)

        page_updates = []
        for item in SQLresult:
            prelink = self.db.get_page_link_by_id(item["id"])
            linkTitle   = item["title"]

            if (linkTitle == None) or (linkTitle == ""):
                # Eine Seite muß nicht zwingent ein Title haben
                linkTitle = item["name"]

            lastupdate = self.tools.convert_date_from_sql(
                item["lastupdatetime"]
            )
            user_id = item["lastupdateby"]
            try:
                user = users[user_id]["name"]
            except KeyError:
                user = "unknown id %s" % user_id

            page_updates.append(
                {
                    "date"  : lastupdate,
                    "link"  : prelink,# + item["name"],
                    "title" : cgi.escape( linkTitle ),
                    "user"  : user,
                }
            )

        context = {
            "page_updates" : page_updates
        }
        #~ self.page_msg(context)

        self.templates.write("PageUpdateTable", context)













