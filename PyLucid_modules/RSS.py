#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__="0.2.2"

__history__="""
v0.2.2
    - Anpassung zum PyLucid Modul
v0.2.1
    - clean up and simplified by Jens Diemer
v0.2
    - Converted by A.Hopek to a CGI - Web Application
v0.1
    - borrowed Code from Mark Pilgrim at http://www.xml.com/pub/a/2002/12/18/dive-into-xml.html?page=last
"""

#~ import cgitb; cgitb.enable()
import xml.dom.minidom
import sys,os, urllib


#_______________________________________________________________________
# Module-Manager Daten


class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "RSS" : {
            "lucidFunction" : "RSS", # <lucidFunction:RSS>'Dateiname'</lucidFunction>
            "must_login"    : False,
            "must_admin"    : False,
        },
    }



#_______________________________________________________________________


class RSS:
    DEFAULT_NAMESPACES = (
        None, # RSS 0.91, 0.92, 0.93, 0.94, 2.0
        'http://purl.org/rss/1.0/', # RSS 1.0
        'http://my.netscape.com/rdf/simple/0.9/' # RSS 0.90
    )
    DUBLIN_CORE = ('http://purl.org/dc/elements/1.1/',)

    def getElementsByTagName( self, node, tagName, possibleNamespaces=DEFAULT_NAMESPACES ):
        for namespace in possibleNamespaces:
            children = node.getElementsByTagNameNS(namespace, tagName)
            if len(children): return children
        return []

    def node_data( self, node, tagName, possibleNamespaces=DEFAULT_NAMESPACES):
        children = self.getElementsByTagName(node, tagName, possibleNamespaces)
        node = len(children) and children[0] or None
        return node and "".join([child.data.encode("utf_8") for child in node.childNodes]) or None

    def get_txt( self, node, tagName, default_txt="" ):
        """
        Liefert den Inhalt >tagName< des >node< zurück, ist dieser nicht
        vorhanden, wird >default_txt< zurück gegeben.
        """
        return self.node_data( node, tagName ) or self.node_data( node, tagName, self.DUBLIN_CORE ) or default_txt

    def print_txt( self, node, tagName, print_string ):
        """
        Formatierte Ausgabe
        """
        item_data = self.get_txt( node, tagName )
        if item_data == "":
            return
        print print_string % {
            "tag"   : tagName,
            "data"  : item_data
        }

    def print_rss( self, url ):
        rssDocument = xml.dom.minidom.parse( urllib.urlopen( url ) )

        for node in self.getElementsByTagName(rssDocument, 'item'):
            print '<ul class="RSS">'

            print '<li><h1><a href="%s">' % self.get_txt( node, "link", "#" )
            print self.get_txt( node, "title", "<no title>" )
            print "</a></h1></li>"

            self.print_txt( node, "date",           '<li><small>%(data)s</li>' )
            self.print_txt( node, "description",    '<li>%(data)s</li>' )
            print "</ul>"


#~ RSS().print_rss( "http://sourceforge.net/export/rss2_projnews.php?group_id=146328" )
#~ print "="*80
#~ RSS().print_rss( "http://www.xml.com/2002/12/18/examples/rss20.xml.txt" )


def PyLucid_action( PyLucid, function_string ):
    # Aktion starten
    RSS().print_rss( function_string )