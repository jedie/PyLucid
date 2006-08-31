#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
A small RSS news feed Generator


not ready to use yet!!!
"""

__version__="0.2"

__history__="""
v0.2
    - Anpassung an PyLucid v0.7
v0.1
    - erste Version
"""


import sys, os, cgi



from PyLucid.system.BaseModule import PyLucidBaseModule


class RSSfeedGenerator(PyLucidBaseModule):

    def lucidTag(self):
        html = '<a href="%s">RSS</a>' % (
            self.URLs.actionLink("download")
        )
        self.response.write(html)

    def download(self):
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
        self.page_msg(context)

        content = self.templates.get("RSSfeed", context)

        self.response.startFileResponse("rss.xml", contentLen=None, \
                    content_type='application/octet-stream; charset=utf-8')
        self.response.write(content)
        return self.response

