#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid Plugin
Blendet RSS-Daten von einem anderen Server in die CMS-Seite ein.
Bsp.:
<lucidFunction:RSS>http://sourceforge.net/export/rss2_projnews.php?group_id=146328</lucidFunction>

Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev:$"

import xml.dom.minidom
import md5, sys, os, urllib, time

import socket
# Timeout setzten, damit Eine Anfrage zu einem nicht erreichbaren Server
# schneller abbricht. Denn ansonsten wird die PyLucid-CMS-Seite lange Zeit
# nicht angezeigt!
socket.setdefaulttimeout(5)


from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.tools.out_buffer import out_buffer
from PyLucid.components.db_cache import DB_Cache, CacheObjectNotFound



class RSS(PyLucidBaseModule):

    info_txt = '<small class="RSS_info">\n\t%s\n</small>\n'

    def lucidFunction(self, function_info):
        db_cache_key = md5.new(function_info).hexdigest()

        db_cache = DB_Cache(self.request, self.response)
        #~ db_cache.delete_object(db_cache_key)

        try:
            rss_page = db_cache.get_object(db_cache_key)
        except CacheObjectNotFound:
            # Die RSS Daten sind noch nicht gecached.

            out = out_buffer(self.page_msg)

            start_time = time.time()
            RSS_Maker(
                out_obj = out,
                rss_url = function_info,
            )
            duration_time = time.time() - start_time
            txt = (
                '[Server response time: %0.2fsec. (incl. render time)]'
            ) % duration_time
            self.response.write(self.info_txt % txt)

            rss_page = out.get()

            # In Cache packen:
            expiry_time = 1 * 60 * 60 # Zeit in Sekunden
            db_cache.put_object(db_cache_key, expiry_time, rss_page)
        else:
            self.response.write(self.info_txt % "[Used cached data]")

        self.response.write(rss_page)


#_____________________________________________________________________________


class RSS_Maker(object):

    DEFAULT_NAMESPACES = (
        None, # RSS 0.91, 0.92, 0.93, 0.94, 2.0
        'http://purl.org/rss/1.0/', # RSS 1.0
        'http://my.netscape.com/rdf/simple/0.9/' # RSS 0.90
    )
    DUBLIN_CORE = ('http://purl.org/dc/elements/1.1/',)

    def __init__(self, out_obj, rss_url):
        self.out_obj = out_obj

        self.feed(rss_url)

    def feed(self, rss_url):
        """
        Diese Funktion wird direkt vom Modul-Manager ausgeführt.
        """
        try:
            rss_data = urllib.urlopen(rss_url)
        except Exception, e:
            self.out_obj.write(
                "[Can't get RSS feed '%s' Error:'%s']" % (rss_url, e )
            )
            return

        rssDocument = xml.dom.minidom.parse(rss_data)

        for node in self.getElementsByTagName(rssDocument, 'item'):
            self.out_obj.write('<ul class="RSS">\n')

            self.out_obj.write(
                '<li><h1><a href="%s">\n' % self.get_txt( node, "link", "#" )
            )
            self.out_obj.write(self.get_txt( node, "title", "<no title>" ))
            self.out_obj.write("</a></h1></li>\n")

            self.print_txt(node, "date", '<li><small>%(data)s</small></li>')
            self.print_txt(node, "description", '<li>%(data)s</li>')
            self.out_obj.write("</ul>")

    def getElementsByTagName(self, node, tagName,
            possibleNamespaces=DEFAULT_NAMESPACES
        ):
        for namespace in possibleNamespaces:
            children = node.getElementsByTagNameNS(namespace, tagName)
            if len(children): return children
        return []

    def node_data( self, node, tagName,
            possibleNamespaces=DEFAULT_NAMESPACES
        ):
        children = self.getElementsByTagName(node, tagName, possibleNamespaces)
        node = len(children) and children[0] or None
        return node and "".join(
            [child.data.encode("utf_8") for child in node.childNodes]
        ) or None

    def get_txt( self, node, tagName, default_txt="" ):
        """
        Liefert den Inhalt >tagName< des >node< zurück, ist dieser nicht
        vorhanden, wird >default_txt< zurück gegeben.
        """
        return self.node_data(node, tagName) or self.node_data(
            node, tagName, self.DUBLIN_CORE
        ) or default_txt

    def print_txt( self, node, tagName, print_string ):
        """
        Formatierte Ausgabe
        """
        item_data = self.get_txt(node, tagName)
        if item_data == "":
            return
        txt = print_string % {
            "tag"   : tagName,
            "data"  : item_data
        }
        self.out_obj.write(txt)
        self.out_obj.write("\n")



