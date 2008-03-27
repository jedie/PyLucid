# -*- coding: utf-8 -*-

"""
    PyLucid cache + page statistics
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A special middleware for caching and page statistics.

    We used our own cache middleware, because:
        - cache only the normal cms page views
        - cache only for anonymous users
        - Build the cache key based on the page shortcuts

    If request.debug == True: We added set response["from_cache"] = "yes" if
    the response comes from the cache.

    The page statistics part bases on:
        http://code.djangoproject.com/wiki/PageStatsMiddleware

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import time, datetime, md5

from django.db import connection
from django.conf import settings
from django.http import HttpResponse
from django.core.cache import cache

from PyLucid.template_addons.filters import human_duration
from PyLucid.models import Page

CACHE_TIMEOUT = settings.CACHE_MIDDLEWARE_SECONDS

# Save the start time of the current running pyhon instance
start_overall = time.time()

TAG = u"<!-- script_duration -->"

FMT = (
    u'render time: %(total_time)s -'
    ' overall: %(overall_time)s -'
    ' queries: %(queries)d'
)

# RFC1123 date format as specified by HTTP RFC2616 section 3.3.1:
# http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.3.1
DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"


def build_cache_key(url):
    """
    -Build the cache_key from the given url. Use the last page shortcut.
    -retuned the cache_key and the page data.
    """
    url = url.strip("/")
    if url == "":
        # default page request
        shortcut = "/"
    else:
        # Use the last shortcut in the url
        # e.g.: '/page1/page2/page3' -> ['/page1/page2', 'page3'] -> 'page3'
        shortcut = url.rsplit("/", 1)[-1]

    cache_key = settings.PAGE_CACHE_PREFIX + shortcut
    return shortcut, cache_key


class CacheMiddleware(object):
    def process_request(self, request):
        """
        -save startistics start values.
        -returned the response from the cache if exists, but only if a anonymous
        user makes a GET or HEAD requests.
        """
        # save start time and the number of db queries before we do anything
        self.start_time = time.time()
        self.old_queries = len(connection.queries)

        # cache only GET or HEAD requests
        if not request.method in ('GET', 'HEAD') or request.GET:
            request._use_cache = False
            return

        # Cache only for anonymous users.
        if request.user.is_anonymous() != True:
            # Don't cache for non anonymous users. Otherwise log-in users don't
            # see the dynamic integrated admin menu.
            request._use_cache = False
            return

        # Build the cache key based on the page shortcuts
        url = request.path
        shortcut, self.cache_key = build_cache_key(url)

        # Get the page data from the cache. If not exist response is None.
        response = cache.get(self.cache_key)

        if response:
            # The page data exist in the cache
            assert isinstance(response, HttpResponse)
            if request.debug:
                #print "Use cached page version. (key: '%s')" % self.cache_key
                response["from_cache"] = "yes"
            self.insert_page_stats(request, response)
        #elif settings.DEBUG:
            #print "Page not in cache found. (key: '%s')" % self.cache_key

        return response


    def process_response(self, request, response):
        """
        Cache the response and insert the page statistics.
        """
        if getattr(request, "_use_cache", False) != True:
            # Don't cache
            self.insert_page_stats(request, response)
            return response

        # cache the response
        self.cache_response(request, response)

        self.insert_page_stats(request, response)

        return response


    def cache_response(self, request, response):
        """
        Cache the given response.
        """
        # Add cache info headers to the response object
        self.patch_response_headers(request, response)

        # Save the page into the cache
        cache.set(self.cache_key, response, CACHE_TIMEOUT)


    def patch_response_headers(self, request, response):
        """
        Adds some useful response headers for the browser cache to the given
        HttpResponse object.
        Based on django.utils.cache.patch_response_headers() but here we use
        the original page last update time.
        """
        # The the original page last update time
        context = request.CONTEXT
        current_page_obj = context["PAGE"]
        lastupdatetime = current_page_obj.lastupdatetime

        response['ETag'] = md5.new(self.cache_key).hexdigest()
        response['Last-Modified'] = lastupdatetime.strftime(DATE_FORMAT)
        now = datetime.datetime.utcnow()
        expires = now + datetime.timedelta(0, CACHE_TIMEOUT)
        response['Expires'] = expires.strftime(DATE_FORMAT)


    def insert_page_stats(self, request, response):
        """
        calculate the statistic and replace it into the html page.
        """
        # Put only the statistic into HTML pages
        if not "html" in response._headers["content-type"][1]:
            # No HTML Page -> do nothing
            return response

        # compute the db time for the queries just run
        # FIXME: In my shared webhosting environment the queries is always = 0
        queries = len(connection.queries) - self.old_queries

        total_time = human_duration(time.time() - self.start_time)
        overall_time = human_duration(time.time() - start_overall)

        # replace the comment if found
        stat_info = FMT % {
            'total_time' : total_time,
            'overall_time' : overall_time,
            'queries' : queries,
        }

        content = response.content
        if not isinstance(content, unicode):
            # FIXME: In my shared webhosting environment is response.content a
            # string and not unicode. Why?
            from django.utils.encoding import force_unicode
            try:
                content = force_unicode(content)
            except:
                return response

        # insert the page statistic
        new_content = content.replace(TAG, stat_info)
        response.content = new_content

        return response
