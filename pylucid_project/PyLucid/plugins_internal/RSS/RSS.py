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

import time, socket

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.utils import escape
from PyLucid.tools import feedparser

from django.core.cache import cache
from django.utils.safestring import mark_safe

UPDATE_INFO = mark_safe(
    'Warning, title argument for RSS Plugin is obsolete! See:'
    ' <a href="http://pylucid.org/_goto/121/changes/#18-07-2008-RSS-plugin-updates">'
    'Backwards-incompatible changes</a>'
)

class RSS(PyLucidBasePlugin):

    def _debug(self, url, feed):
        from pprint import pformat
        self.response.write("<h2>RSS debug for '%s':</h2>\n" % url)
        self.response.write("<pre>\n")
        self.response.write(escape(pformat(feed)))
        self.response.write("</pre>\n")

    def lucidTag(self, url, internal_page=None, debug=None, pref_id=None, title=None):

        if self.request.debug:
            if title:
                # title tag is obsolete
                self.page_msg(UPDATE_INFO)

        # Get the preferences from the database:
        if pref_id:
            preferences = self.get_preferences(id = pref_id)
        else:
            # get the default entry
            preferences = self.get_preferences()

        if preferences == None:
            self.page_msg.red("Can't get preferences from database.")
            return

        if internal_page == None:
            internal_page = preferences["internal_page"]
        if debug == None:
            debug = preferences["debug"]

#        rss_page = cache.get(url)
#        if rss_page:
#            self.response.write(self.info_txt % "[Used cached data]")
#        else:
            # Was not cached

        start_time = time.time()

        timeout = preferences.get("timeout", 1)
        try:
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            feed = feedparser.parse(url)
            socket.setdefaulttimeout(old_timeout)
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
        self._render_template(internal_page, context)#, debug=True)

