# coding: utf-8

from django import http
from django.conf import settings
from django.core.cache import cache
from Cookie import SimpleCookie
from django.utils.cache import get_max_age, patch_response_headers
from django.http import HttpResponse

def has_messages(request):
    if hasattr(request, '_messages') and len(request._messages) != 0:
        return True
    return False

class PyLucidCacheMiddlewareBase(object):
    def use_cache(self, request):
        if not request.method in ('GET', 'HEAD'):
            #print "cache not %r" % request.method
            return False
        if request.GET:
            # Don't cache PyLucid get views
            return False
        if settings.RUN_WITH_DEV_SERVER and request.path.startswith(settings.MEDIA_URL):
            # Don't cache static files in dev server
            return False

        if request.user.is_authenticated():
            # Don't cache user-variable requests from authenticated users.
            return False

        if has_messages(request):
            # Don't cache pages for anonymous users which contains a messages
            #print "*** page for anonymous users has messages -> don't cache"
            return False

        return True

class PyLucidFetchFromCacheMiddleware(PyLucidCacheMiddlewareBase):
    def process_request(self, request):
        """
        Try to fetch response from cache, if exists.
        """
        if not self.use_cache(request):
            #print "Don't fetch from cache."
            return

        cache_key = request.path
        response = cache.get(cache_key)
        if response is not None: # cache hit
            #print "Use %r from cache!" % cache_key
            response._from_cache = True
            return response

class PyLucidUpdateCacheMiddleware(PyLucidCacheMiddlewareBase):
    def process_response(self, request, response):
        if getattr(response, "_from_cache", False) == True:
            # Current response comes from the cache, no need to update the cache
            return response

        if response.status_code != 200: # Don't cache e.g. error pages
            return response

        if not self.use_cache(request):
            #print "Don't put to cache."
            return response

        # get the timeout from the "max-age" section of the "Cache-Control" header
        timeout = get_max_age(response)
        if timeout == None:
            # use default cache_timeout
            timeout = settings.CACHE_MIDDLEWARE_SECONDS
        elif timeout == 0:
            # Don't cache this page
            return response

        # Create a new HttpResponse for the cache, so we can skip existing
        # cookies and attributes like response.csrf_processing_done
        response2 = HttpResponse(
            content=response._container,
            status=200,
            content_type=response['Content-Type']
        )

        # Adds ETag, Last-Modified, Expires and Cache-Control headers
        patch_response_headers(response2, timeout)

        cache_key = request.path
        cache.set(cache_key, response2, timeout)

        #print "PyLucidUpdateCacheMiddleware.process_response send cookies:", response.cookies
        return response
