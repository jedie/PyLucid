#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid Plugin
Blendet RSS-Daten von einem anderen Server in die CMS-Seite ein.
Bsp.:
<lucidFunction:RSS>http://sourceforge.net/export/rss2_projnews.php?group_id=146328</lucidFunction>
"""

__version__="0.2.7"

__history__="""
v0.2.7
    - Zeit die response time an
    - Aufgeräumt
v0.2.6
    - lucidFunction() erwartet nun auch function_info vom ModulManager
v0.2.5
    - Umbau für neuen Module-Manager
    - Ab jetzt ist es ein Plugin ;)
v0.2.4
    - Timeout beim empfangen des RSS feeds eingebaut (ab Python 2.3)
v0.2.3
    - Bug: <small>-Tag wurde beim Datum nicht geschlossen
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
import sys, os, urllib, time




#_______________________________________________________________________


class RSS:

    DEFAULT_NAMESPACES = (
        None, # RSS 0.91, 0.92, 0.93, 0.94, 2.0
        'http://purl.org/rss/1.0/', # RSS 1.0
        'http://my.netscape.com/rdf/simple/0.9/' # RSS 0.90
    )
    DUBLIN_CORE = ('http://purl.org/dc/elements/1.1/',)

    def __init__( self, PyLucid ):
        # Es werden keine PyLucid-Objekte benötigt...
        pass

    def lucidFunction( self, function_info ):
        """
        Diese Funktion wird direkt vom Modul-Manager ausgeführt.
        """
        url = function_info
        try:
            import socket
            socket.setdefaulttimeout(5)
        except AttributeError:
            # Geht erst ab Python 2.3 :(
            pass

        start_time = time.time()
        try:
            rss_data = urllib.urlopen( url )
        except Exception, e:
            print "[Can't get RSS feed '%s' Error:'%s']" % ( url, e )
            return
        duration_time = time.time() - start_time
        print '<small class="RSS_info">(response time: %0.2fsec.)</small>' % duration_time

        rssDocument = xml.dom.minidom.parse( rss_data )

        for node in self.getElementsByTagName(rssDocument, 'item'):
            print '<ul class="RSS">'

            print '<li><h1><a href="%s">' % self.get_txt( node, "link", "#" )
            print self.get_txt( node, "title", "<no title>" )
            print "</a></h1></li>"

            self.print_txt( node, "date",           '<li><small>%(data)s</small></li>' )
            self.print_txt( node, "description",    '<li>%(data)s</li>' )
            print "</ul>"

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

if __name__ == "__main__":
    RSS("").lucidFunction( "http://sourceforge.net/export/rss2_projnews.php?group_id=146328" )
    #~ print "="*80
    RSS("").lucidFunction( "http://jensdiemer.de/RSS" )
