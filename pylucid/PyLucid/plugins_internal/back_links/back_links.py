#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
<lucidTag:back_links/>
Generiert eine horizontale zurück-Linkleiste

Created by Jens Diemer

GPL-License
"""

import cgi

from PyLucid.system.BasePlugin import PyLucidBasePlugin

from PyLucid.models import Page

class back_links(PyLucidBasePlugin):
    indexlink = '<a href="/">Index</a>'
    backlink  = '<a href="%(url)s">%(title)s</a>'

    def lucidTag( self ):
        """
        generate the backlinks
        """
        current_page = self.context["PAGE"]
        parent_page = current_page.parent
        if not parent_page: # No higher-ranking page
            return ""

        data = self.backlink_data(parent_page)
        data.reverse()
        self.make_links(data)

    def backlink_data(self, parent_page):
        """
        get the link data from the db
        """
        data = []
        urls = [""]

        while parent_page:
            page_id = parent_page.id
            page = Page.objects.get(id=page_id)
            urls.append(page.shortcut)

            title = page.title
            if title in (None, ""):
                title = page.name

            data.append({
                    "title": title,
                    "url": "/".join(urls),
            })
            parent_page = page.parent
        return data

    def make_links(self, data):
        """
        write the links directly into the page
        """
        self.response.write(self.indexlink)

        for link_data in data:
            link = self.backlink % {
                "url": link_data["url"],
                "title": cgi.escape( link_data["title"] ),
            }
            self.response.write(" &gt; %s" % link)







