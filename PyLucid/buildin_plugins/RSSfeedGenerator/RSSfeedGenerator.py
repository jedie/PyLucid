#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
A small RSS news feed Generator

Info:
If this plugin is installed, you can insert this Link in the global Template:

<link rel="alternate" type="application/rss+xml" title="RSS" \
href="/_command/RSSfeedGenerator/download/RSS.xml" />

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


import sys, os, cgi, time

RSS_filename = "RSS.xml"

#~ debug = True
debug = False

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
        page_updates = self.db.get_page_update_info(15)

        context = {
            "page_updates" : page_updates,
            "homepage_link" : self.URLs["absoluteIndex"],
            "hostname": self.URLs["hostname"],
            "pubDate": time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
        }
        if debug:
            self.page_msg("RSSfeedGenerator - Debug context:")
            self.page_msg(context)

        content = self.templates.get_rendered_page("RSSfeed", context)

        #~ self.response.startFileResponse(RSS_filename, contentLen=None, \
                    #~ content_type='application/rss+xml; charset=utf-8')
        #~ self.response.write(content)
        #~ return self.response

        if debug:
            self.response.write("<h2>Debug:</h2><pre>")
            self.response.write(cgi.escape(content))
            self.response.write("</pre>")
        else:
            # XML Datei senden
            self.response.startFreshResponse(content_type="application/xml")
            self.response.write(content)
            return self.response
