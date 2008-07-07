# -*- coding: utf-8 -*-

"""
    PyLucid RSS plugin
    ~~~~~~~~~~~~~~~~~~

    Include external RSS Feeds directly into a CMS page.
    Used feedparser by Mark Pilgrim: http://feedparser.org
    http://feedparser.googlecode.com/svn/trunk/LICENSE

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

__version__= "$Rev$"

import time

import socket
# Timeout setzten, damit Eine Anfrage zu einem nicht erreichbaren Server
# schneller abbricht. Denn ansonsten wird die PyLucid-CMS-Seite lange Zeit
# nicht angezeigt!
socket.setdefaulttimeout(5)


from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools import feedparser

from django.core.cache import cache
from django.utils.safestring import mark_safe

class RSS(PyLucidBasePlugin):

    def _debug(self, url, feed):
        from pprint import pformat
        self.response.write("<h2>RSS debug for '%s':</h2>\n" % url)
        self.response.write("<pre>\n")
        self.response.write(pformat(feed))
        self.response.write("</pre>\n")

    def lucidTag(self, url, debug=False, title=None):
#        rss_page = cache.get(url)
#        if rss_page:
#            self.response.write(self.info_txt % "[Used cached data]")
#        else:
            # Was not cached

        start_time = time.time()

        try:
            feed = feedparser.parse(url)
        except Exception, e:
            self.response.write(
                "[Can't get RSS feed '%s' Error:'%s']" % (url, e )
            )
            return

#            cache.set(url, rss_page)

        duration = time.time() - start_time

        if debug:
            self._debug(url, feed)

        context = {
            "url": url,
            "feed": feed,
            "duration": duration,
        }
        self._render_template("RSS", context)#, debug=True)

