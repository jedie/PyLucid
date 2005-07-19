#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert das SiteMap
<lucidTag:SiteMap/>
"""

__version__="0.0.2"

__history__="""
v0.0.2
    - "must_login" und "must_admin" für Module-Manager hinzugefügt
v0.0.1
    - erste Version
"""


import urllib


#_______________________________________________________________________
# Module-Manager Daten

class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "SiteMap" : {
            "lucidTag"      : "SiteMap",
            "must_login"    : False,
            "must_admin"    : False,
        }
    }


#_______________________________________________________________________


class SiteMap:
    def __init__( self, PyLucid_objects ):
        self.db = PyLucid_objects["db"]
        self.config = PyLucid_objects["config"]

        self.link  = '<a href="'
        self.link += self.config.system.poormans_url + self.config.system.page_ident
        self.link += '%(link)s">%(name)s</a>'

    def action( self ):
        """ Baut die SiteMap zusammen """
        self.data = self.db.get_sitemap_data()

        self.parent_list = self.get_parent_list()
        #~ return str( self.parent_l    ist )

        self.page = '<div id="SiteMap">'
        self.make_sitemap()
        self.page += '</div>'
        return self.page

    def get_parent_list( self ):
        parents = []
        for site in self.data:
            if not site["parent"] in parents:
                parents.append( site["parent"] )
        return parents

    def make_sitemap( self, parentname = "", id = 0, deep = 0 ):
        self.page += '<ul>\n'
        for site in self.data:
            if site["parent"] == id:
                self.page += '<li class="deep_%s">' % deep

                self.page += self.link % {
                    "link"  : urllib.quote( parentname + "/" + site["name"] ),
                    "name"  : site["name"],
                }

                if (site["title"] != None) and (site["title"] != ""):
                    self.page += " - %s" % site["title"]

                self.page += "</li>\n"

                if site["id"] in self.parent_list:
                    self.make_sitemap( parentname + "/" + site["name"], site["id"], deep +1 )

        self.page += "</ul>\n"


#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid_objects ):
    # Aktion starten
    return SiteMap( PyLucid_objects ).action()






