# -*- coding: utf-8 -*-

"""
    PyLucid RSS news feed generator plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    example for a html link:
        <a href="{% lucidTag RSSfeedGenerator count="10" %}"
        type="application/rss+xml" title="page updates">RSS feed</a>

    example for the html head:
        <link rel="alternate" type="application/rss+xml" title="page updates"
        href="{% lucidTag RSSfeedGenerator count="10" %}" />

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import sys, os, cgi, time, inspect

RSS_FILENAME = "RSS.xml"

from django.http import HttpResponse
from django.core.cache import cache

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.system.exceptions import PluginError
from PyLucid import PYLUCID_VERSION_STRING
from PyLucid.models import Plugin



# Same key used by the PageUpdateList Plugin, too!!!
CACHE_KEY = "page_updates_data"

#debug = True
debug = False









class RSSfeedGenerator(PyLucidBasePlugin):

    def feed(self):
        if self.request.user.is_staff:
            hide_non_public = False
        else:
            hide_non_public = True

        page_updates = Page.objects.get_update_info(hide_non_public)
        page_updates = page_updates[:count]

    def lucidTag(self, count=10):
        """
        returned the link to the feed, with a count GET parameter.
        """
        plugins = Plugin.objects.method_filter(
            queryset = Plugin.objects.filter(active=True),
            method_name="feed",
            page_msg=self.page_msg, verbosity=1
        )
        for plugin in plugins:
            self.page_msg(plugin)


        return



        count = self._prepare_count(count)
        link = self.URLs.methodLink("download")
        url = "%s%s?count=%s" % (link, RSS_FILENAME, count)
        return url

    def _get_feed(self):
        count = self.request.GET.get("count", 10)
        count = self._prepare_count(count)
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

        if self.request.user.is_staff:
            hide_non_public = False
        else:
            hide_non_public = True

        page_updates = Page.objects.get_update_info(hide_non_public)
        page_updates = page_updates[:count]

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

    def _prepare_count(self, count):
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


