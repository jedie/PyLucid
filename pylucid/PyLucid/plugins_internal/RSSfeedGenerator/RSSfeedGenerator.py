#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid RSS news feed generator plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    -With {% lucidTag RSSfeedGenerator count=10 %} you can generate a link to
    the RSS XML file.

    FIXME: Make the "count" argument not as a GET parameter.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


import sys, os, cgi, time

RSS_FILENAME = "RSS.xml"

#debug = True
debug = False

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.db.page import get_update_info
from PyLucid.system.exceptions import PluginError
from PyLucid import PYLUCID_VERSION_STRING

from django.http import HttpResponse

from django.core.cache import cache
# Same key used by the PageUpdateList Plugin, too!!!
CACHE_KEY = "page_updates_data"

class RSSfeedGenerator(PyLucidBasePlugin):

    def lucidTag(self, count=10):
        """
        Put a link to the RSS feed file into the cms page.
        """
        count = self.prepare_count(count)
        url = self.URLs.methodLink("download")
        url = url + RSS_FILENAME

        # FIXME: We should better use a small internal page for this:
        html = (
            '<a href="%s?count=%s" type="application/rss+xml" title="RSS">'
            'RSS'
            '</a>'
        ) % (url, count)
        self.response.write(html)

        # TODO: implement a way to add this into the html head:
#        headLink = (
#            '<link rel="alternate" type="application/rss+xml"'
#            ' title="RSS" href="%s" />\n'
#        ) % url
#        self.response.addCode.insert(headLink)

    def _get_feed(self):
        count = self.request.GET.get("count", 10)
        count = self.prepare_count(count)
        cache_key = "%s_%s" % (CACHE_KEY, count)
        if debug:
            self.page_msg("RSSfeedGenerator Debug:")
            self.page_msg("count:", count)
            self.page_msg("cache_key:", cache_key)

        context = {}

        if self.request.user.is_anonymous():
            # Use only the cache for anonymous users.
            content = cache.get(cache_key)
            if content:
                return content

        page_updates = get_update_info(self.context, count)

        context = {
            "page_updates": page_updates,
            "homepage_link": self.URLs["absoluteIndex"],
            "hostname": self.URLs["hostname"],
            "pylucid_version": PYLUCID_VERSION_STRING,
            "pubDate": time.strftime(
                "%a, %d %b %Y %H:%M:%S +0000", time.gmtime()
            ),
        }

        if debug:
            self.page_msg("Debug context:")
            self.page_msg(context)

        content = self._get_rendered_template("RSSfeed", context)

        cache.set(cache_key, content, 120)

        return content

    def download(self, filename):
        """
        Generate the XML file and send it to the client.
        Info: the method ignored the filename
        """
        content = self._get_feed()

        if debug:
            self.response.write("<h2>Debug:</h2><pre>")
            self.response.write(cgi.escape(content))
            self.response.write("</pre>")
            return

        # send the XML file to the client
        response = HttpResponse()
        response['Content-Type'] = 'application/xml; charset=utf-8'
        response.write(content)
        return response

    def prepare_count(self, count):
        """
        Check if the count is a number and in a definied range.
        """
        try:
            count = int(count)
            if count<1 or count>100:
                raise AssertionError("Number is out of range.")
            return count
        except Exception, e:
            msg = "Error! Wrong count argument: %s" % e
            raise PluginError(msg)
