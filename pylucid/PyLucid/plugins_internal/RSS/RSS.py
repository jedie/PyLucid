#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid Plugin
Blendet RSS-Daten von einem anderen Server in die CMS-Seite ein.
Bsp.:
<lucidFunction:RSS>http://sourceforge.net/export/rss2_projnews.php?group_id=146328</lucidFunction>

Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev$"

import xml.dom.minidom
import md5, sys, os, urllib, time

import socket
# Timeout setzten, damit Eine Anfrage zu einem nicht erreichbaren Server
# schneller abbricht. Denn ansonsten wird die PyLucid-CMS-Seite lange Zeit
# nicht angezeigt!
socket.setdefaulttimeout(5)


from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.system.response import SimpleStringIO
from django.core.cache import cache



class RSS(PyLucidBasePlugin):

    info_txt = '<small class="RSS_info">\n\t%s\n</small>\n'

    def lucidTag(self, url, title):

#        rss_page = cache.get(url)
#        if rss_page:
#            self.response.write(self.info_txt % "[Used cached data]")
#        else:
            # Was not cached

        start_time = time.time()

        try:
            rss_data = urllib.urlopen(url)
        except Exception, e:
            self.page_msg.red(
                "[Can't get RSS feed '%s' Error:'%s']" % (url, e )
            )
            return

#            cache.set(url, rss_page)

        server_response = time.time() - start_time

        start_time = time.time()
        r = RSS_Maker()
        data = r.feed(rss_data)
        paser_duration = time.time() - start_time

        context = {
            "url": url,
            "title": title,
            "entries": data,
            "server_response": server_response,
            "paser_duration": paser_duration,
        }
        self._render_template("RSS", context)#, debug=True)


#_____________________________________________________________________________

DEFAULT_NAMESPACES = (
    None, # RSS 0.91, 0.92, 0.93, 0.94, 2.0
    'http://purl.org/rss/1.0/', # RSS 1.0
    'http://my.netscape.com/rdf/simple/0.9/' # RSS 0.90
)
DUBLIN_CORE = ('http://purl.org/dc/elements/1.1/',)

class RSS_Maker(object):

    def feed(self, rss_data):
        """
        Diese Funktion wird direkt vom Modul-Manager ausgeführt.
        """
        rssDocument = xml.dom.minidom.parse(rss_data)

        entries = []
        for node in self.getElementsByTagName(rssDocument, 'item'):
            entry_data = {
                "title_link": self.get_txt(node, "link", "#"),
                "title": self.get_txt(node, "title", None),
                "date": self.get_txt(node, "date", None),
                "description": self.get_txt(node, "description", None),
            }
            entries.append(entry_data)
        return entries


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

    def get_txt(self, node, tagName, default_txt=""):
        """
        Liefert den Inhalt >tagName< des >node< zurück, ist dieser nicht
        vorhanden, wird >default_txt< zurück gegeben.
        """
        return self.node_data(node, tagName) or self.node_data(
            node, tagName, DUBLIN_CORE
        ) or default_txt


class FeedError(Exception):
    pass
