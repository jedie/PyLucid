# -*- coding: utf-8 -*-

"""
    PyLucid cache + page statistics
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A special middleware for caching and page statistics.

    We used our own cache middleware, because:
        - cache only the normal cms page views
        - cache only for anonymous users
        - Build the cache key based on the page shortcuts

    If request.debug == True: We added added information about the cache status
    in _insert_cache_info():
        - set response["from_cache"] to "yes" / "no" (Not True/False!)
        - Replace the pagestats TAG with cache debug information.

    The page statistics part bases on:
        http://code.djangoproject.com/wiki/PageStatsMiddleware

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import datetime, md5

from django.conf import settings
from django.http import HttpResponse
from django.core.cache import cache

from PyLucid.tools.shortcuts import verify_shortcut
from PyLucid.middlewares.pagestats import TAG

CACHE_TIMEOUT = settings.CACHE_MIDDLEWARE_SECONDS

CACHED_INFO_YES = u"from cache"
CACHED_INFO_NO = u"not cached"

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

    # Check a shortcut. A AssertionError whould be raised if something seems to
    # be wrong.
    # Normaly the url-re of the index view filters bad things out. But
    # process_request in the middleware whould becalled before this done.
    verify_shortcut(shortcut)

    cache_key = settings.PAGE_CACHE_PREFIX + shortcut
    return shortcut, cache_key


class CacheMiddleware(object):
    def __init__(self):
        self.cache_key = None

    def process_request(self, request):
        """
        -save startistics start values.
        -returned the response from the cache if exists, but only if a anonymous
        user makes a GET or HEAD requests.
        """
        request._from_cache = False

        # cache only GET or HEAD requests
        if not request.method in ('GET', 'HEAD') or request.GET:
            request._use_cache = False
            return

        # Cache only for anonymous users.
        if request.user.is_anonymous() != True:
            # If request hasn't the attribute user, the session middleware
            # doen's work. This apperars if there exist no database tables.
            # Don't cache for non anonymous users. Otherwise log-in users don't
            # see the dynamic integrated admin menu.
            request._use_cache = False
            return

        # Build the cache key based on the page shortcuts
        url = request.path
        try:
            shortcut, self.cache_key = build_cache_key(url)
        except AssertionError, e:
            # Something is wrong with the given url
            request._use_cache = False
            return

        # Get the page data from the cache. If not exist response is None.
        response = cache.get(self.cache_key)

        if response == None:
            # The page data doesn't exist in the cache
            return

        # The page data exist in the cache
        assert isinstance(response, HttpResponse)
        request._from_cache = True

        if request.debug:
            # Add the cache debug information.
            response = self._insert_cache_info(request, response, True)

        return response


    def process_response(self, request, response):
        """
        Cache the response and insert the page statistics.
        """
        if request._from_cache == True:
            # The content comes from the cache
            return response

        if getattr(request, "_use_cache", False) != True:
            # Don't cache
            response = self._insert_cache_info(request, response, False)
            return response

        # cache the response
        self._cache_response(request, response)

        response = self._insert_cache_info(request, response, False)

        return response


    def _insert_cache_info(self, request, response, is_from_cache):
        """
        Add the cache debug information.

        if request.debug == True, we added the information if the response
        was from the cache or not. We "added" the information after the
        pagestats >TAG< ;)
        """
        if request._from_cache == True:
            response_msg = CACHED_INFO_YES
            response["from_cache"] = "yes"
        elif request._from_cache == False:
            response_msg = CACHED_INFO_NO
            response["from_cache"] = "no"
        else:
            raise AssertionError("wrong request._from_cache info.")

        content = response.content
        if not isinstance(content, unicode):
            # FIXME: In my shared webhosting environment is response.content a
            # string and not unicode. Why?
            from django.utils.encoding import force_unicode
            try:
                content = force_unicode(content)
            except:
                return response

        # Replace the pagestats TAG with the cache debug information.
        message = u"%s - %s - cache key: %s" % (
            TAG, response_msg, self.cache_key
        )
        new_content = content.replace(TAG, message)
        response.content = new_content

        return response


    def _cache_response(self, request, response):
        """
        Cache the given response.
        """
        # Add cache info headers to the response object
        self._patch_response_headers(request, response)

        # Save the page into the cache
        cache.set(self.cache_key, response, CACHE_TIMEOUT)


    def _patch_response_headers(self, request, response):
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
