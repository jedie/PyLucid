#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
A small RSS news feed Generator

Info:
If this plugin is installed, you can insert this Link in the global Template:

<link rel="alternate" type="application/rss+xml" title="RSS" \
href="/_command/RSSfeedGenerator/download/RSS.xml" />
"""

__version__="0.2.1"

__history__="""
v0.2.1
    - It's running!
v0.2
    - Anpassung an PyLucid v0.7
v0.1
    - erste Version
"""


import sys, os, cgi, time

RSS_filename = "RSS.xml"

from PyLucid.system.BaseModule import PyLucidBaseModule


class RSSfeedGenerator(PyLucidBaseModule):

    def lucidTag(self):
        url = self.URLs.actionLink("download") + RSS_filename
        html = (
            '<a href="%s"'
            ' type="application/rss+xml" title="RSS">'
            'RSS'
            '</a>'
        ) % url
        self.response.write(html)

        headLink = (
            '<link rel="alternate" type="application/rss+xml"'
            ' title="RSS" href="%s" />\n'
        ) % url
        self.response.addCode.insert(headLink)

    def download(self, function_info):
        """
        Generiert den feed und sendet ihn zum Client.
        (function_info wird ignoriert)
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
            link = self.URLs.absoluteLink(prelink)
            linkTitle   = item["title"]

            if linkTitle in (None, ""):
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
                    "link"  : link,# + item["name"],
                    "title" : cgi.escape( linkTitle ),
                    "user"  : user,
                }
            )

        context = {
            "page_updates" : page_updates,
            "homepage_link" : self.URLs["absoluteIndex"],
            "hostname": self.URLs["hostname"],
            "pubDate": time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
        }
        #~ self.page_msg(context)

        content = self.templates.get("RSSfeed", context)

        #~ self.response.startFileResponse(RSS_filename, contentLen=None, \
                    #~ content_type='application/rss+xml; charset=utf-8')
        #~ self.response.write(content)
        #~ return self.response

        self.response.startFreshResponse(content_type="application/xml")
        self.response.write(content)
        return self.response

