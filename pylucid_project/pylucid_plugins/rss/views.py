# -*- coding: utf-8 -*-

"""
    PyLucid RSS plugin
    ~~~~~~~~~~~~~~~~~~

    :copyleft: 2007-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import time
import socket
import traceback
from pprint import pformat

try:
    import feedparser
except ImportError, err:
    feedparser_available = False
    feedparser_err = err
else:
    feedparser_available = True

from django.contrib import messages
from django.core.cache import cache
from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.markup import hightlighter
from pylucid_project.apps.pylucid.decorators import render_to
from pylucid_project.utils.escape import escape

from rss.preference_forms import PreferencesForm

@render_to()#, debug=True)
def lucidTag(request, url, max_entries=None, debug=False, **kwargs):
    """
    Include external RSS Feeds directly into a CMS page.
    
    optional keyword arguments are every db preferences form attribute.
    
    To create a custom template, used the debug mode: Add debug=True in tag.
    Debug mode only works for stuff users.
    
    Used feedparser by Mark Pilgrim: http://feedparser.org
    http://feedparser.googlecode.com/svn/trunk/LICENSE
    
    example:
        {% lucidTag rss url="http url" %}
        {% lucidTag rss url="http url" template_name="rss/MyOwnTemplate.html" %}
        {% lucidTag rss url="http url" max_entries=5 %}
        {% lucidTag rss url="http url" socket_timeout=3 %}
        {% lucidTag rss url="http url" debug=True %}
    """
    if feedparser_available == False:
        if request.user.is_staff:
            messages.error(request, "External 'feedparser' module not available: %s" % err)
            messages.info(request, "PyPi url: http://pypi.python.org/pypi/FeedParser/")
        return "[RSS feed error.]"

    # Get preferences from DB and update them with given kwargs.
    pref_form = PreferencesForm()
    preferences = pref_form.get_preferences(request, lucidtag_kwargs=kwargs)

    cache_key = "rss_feed_%s" % url
    feed_dict = cache.get(cache_key)
    if feed_dict:
        from_cache = True
    else:
        from_cache = False

        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(preferences["socket_timeout"])

        start_time = time.time()
        try:
            feed = feedparser.parse(url)
            if "bozo_exception" in feed:
                if isinstance(feed["bozo_exception"], feedparser.ThingsNobodyCaresAboutButMe):
                    if request.user.is_staff:
                        messages.info(request, "RSS feed info:", feed["bozo_exception"])
                else:
                    raise AssertionError("Feed error: %r" % feed["bozo_exception"])
        except Exception, e:
            if request.user.is_staff:
                messages.debug(request, mark_safe("Feed error:<pre>%s</pre>" % traceback.format_exc()))
                return "[feedparser.parse(%r) error: %s]" % (url, e)
            else:
                return "[Can't get RSS feed.]"

        duration = time.time() - start_time

        socket.setdefaulttimeout(old_timeout)

        feed_dict = {
            "feed": feed,
            "duration": duration,
        }
        cache.set(cache_key, feed_dict, preferences["cache_timeout"])

    if debug and request.user.is_staff:
        messages.info(request, "RSS debug is on, see page content.")
        feed_code = pformat(feed_dict["feed"])
        feed_html = hightlighter.make_html(
            feed_code, source_type="py", django_escape=True
        )
        return "<h1>RSS debug</h1><h2>Feed %r</h2>\n%s" % (url, feed_html)

    if max_entries:
        feed_dict["feed"].entries = feed_dict["feed"].entries[:max_entries]

    context = {
        "template_name": preferences["template_name"],
        "url": url,
        "max_entries": max_entries,
        "feed": feed_dict["feed"],
        "duration": feed_dict["duration"],
        "from_cache": from_cache,
        "preferences": preferences,
    }
    return context
