#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert das SiteMap
<lucidTag:SiteMap/>
"""

__version__="0.2"

__history__="""
v0.2
    - Benutzt ein jinja-Template
v0.1
    - PyLucid["URLs"]
    - Anpassung an neuen ModuleManager
v0.0.5
    - Link wird nun auch vom ModulManager verwendet.
    - Testet page-title auch auf None
v0.0.4
    - Anpassung an neuen ModulManager
v0.0.3
    - Neue Tags für CSS
v0.0.2
    - "must_login" und "must_admin" für Module-Manager hinzugefügt
v0.0.1
    - erste Version
"""

from PyLucid.system.BaseModule import PyLucidBaseModule

class SiteMap(PyLucidBaseModule):

    def lucidTag(self):
        """ Baut die SiteMap zusammen """
        self.data = self.db.get_sitemap_data()

        self.parent_list = self.get_parent_list()

        sitemap = self.make_sitemap()

        context = {
            "sitemap" : sitemap
        }
        #~ self.page_msg(context)

        self.templates.write("SiteMap", context)

    def get_parent_list(self):
        parents = []
        for site in self.data:
            if not site["parent"] in parents:
                parents.append(site["parent"])
        return parents

    def make_sitemap(self, parentname = "", id = 0, deep = 0):
        result = []

        for site in self.data:
            if site["parent"] == id:
                link = "%s/%s" % (parentname, site["shortcut"])
                linkURL = self.URLs.pageLink(link)

                if site["title"] in ("", None):
                    site["title"] == site["name"]

                page_data = {
                    "href"  : linkURL,
                    "name"  : site["name"],
                    "title" : site["title"],
                    "id"    : site["id"],
                    "deep"  : deep,
                }

                if site["id"] in self.parent_list:
                    subitems = self.make_sitemap(link, site["id"], deep +1)
                    page_data["subitems"] = subitems

                result.append(page_data)

        return result






