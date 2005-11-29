#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert das SiteMap
<lucidTag:SiteMap/>
"""

__version__="0.0.5"

__history__="""
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

import cgitb;cgitb.enable()
import cgi, urllib




class SiteMap:

    #_______________________________________________________________________
    # Module-Manager Daten

    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "lucidTag" : {
            "must_login"    : False,
            "must_admin"    : False,
        }
    }

    #_______________________________________________________________________

    def __init__( self, PyLucid ):
        self.db         = PyLucid["db"]
        self.config     = PyLucid["config"]
        self.page_msg   = PyLucid["page_msg"]

    def lucidTag( self ):
        """ Baut die SiteMap zusammen """
        self.data = self.db.get_sitemap_data()

        self.parent_list = self.get_parent_list()
        #~ return str( self.parent_l    ist )

        self.link  = '<a href="'
        self.link += self.link_url
        self.link += '%(link)s">%(name)s</a>'

        print '<div id="SiteMap">'
        self.make_sitemap()
        print '</div>'

    def get_parent_list( self ):
        parents = []
        for site in self.data:
            if not site["parent"] in parents:
                parents.append( site["parent"] )
        return parents

    def make_sitemap( self, parentname = "", id = 0, deep = 0 ):
        print '<ul class="id_%s deep_%s">\n' % ( id, deep )
        for site in self.data:
            if site["parent"] == id:
                print '<li class="id_%s deep_%s">' % ( site["id"], deep )

                link = "%s/%s" % ( parentname, urllib.quote_plus( site["name"] ) )

                print self.link % {
                    "link"  : link,
                    "name"  : cgi.escape( site["name"] ),
                }

                if (site["title"] != "") and (site["title"] != None) and (site["title"] != site["name"]):
                    print " - %s" % cgi.escape( site["title"] )

                print "</li>\n"

                if site["id"] in self.parent_list:
                    self.make_sitemap( link, site["id"], deep +1 )

        print "</ul>\n"






