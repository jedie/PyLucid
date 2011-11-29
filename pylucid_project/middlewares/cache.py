# coding: utf-8

from django import http
from django.conf import settings
from django.core.cache import cache
from Cookie import SimpleCookie
from django.utils.cache import get_max_age, patch_response_headers
from django.http import HttpResponse
import sys
from django.utils.log import getLogger
from django.contrib import messages


logger = getLogger("PyLucidCacheMiddleware")
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())



class PyLucidCacheMiddlewareBase(object):
    def use_cache(self, request):
        if not request.method in ('GET', 'HEAD'):
            logger.debug("Don't cache %r" % request.method)
            return False
        if request.GET:
            # Don't cache PyLucid get views
            logger.debug("Don't cache request with GET parameter: %s" % repr(request.GET))
            return False
        if settings.RUN_WITH_DEV_SERVER and request.path.startswith(settings.MEDIA_URL):
            logger.debug("Don't cache static files in dev server")
            return False

        if request.user.is_authenticated():
            logger.debug("Don't cache user-variable requests from authenticated users.")
            return False

        if hasattr(request, '_messages') and len(request._messages) != 0:
            storage = messages.get_messages(request)
            raw_messages = ", ".join([message.message for message in storage])
            storage.used = False

            logger.debug("Don't cache page, it has this messages: %s" % raw_messages)
            #print "*** page for anonymous users has messages -> don't cache"
            return False

        return True

    def get_cache_key(self, request):
        """
        Build the cache key based on the url and:
        
        * LANGUAGE_CODE: The language code in the url can be different than the
            used language for gettext translation.
        * SITE_ID: request.path is the url without the domain name. So the same
            url in site A and B would result in a collision.
        """
        path = request.path

        try:
            language_code = request.LANGUAGE_CODE # set in django.middleware.locale.LocaleMiddleware
        except AttributeError:
            etype, evalue, etb = sys.exc_info()
            evalue = etype("%s (django.middleware.locale.LocaleMiddleware must be insert before cache middleware!)" % evalue)
            raise etype, evalue, etb

        site_id = settings.SITE_ID
        cache_key = "%s:%s:%s" % (path, language_code, site_id)
        logger.debug("Cache key: %r" % cache_key)
        return cache_key


class PyLucidFetchFromCacheMiddleware(PyLucidCacheMiddlewareBase):
    def process_request(self, request):
        """
        Try to fetch response from cache, if exists.
        """
        if not self.use_cache(request):
            #print "Don't fetch from cache."
            return

        cache_key = self.get_cache_key(request)
        response = cache.get(cache_key)
        if response is not None: # cache hit
            logger.debug("Use %r from cache!" % cache_key)
            response._from_cache = True
            return response


class PyLucidUpdateCacheMiddleware(PyLucidCacheMiddlewareBase):
    def process_response(self, request, response):
        if getattr(response, "_from_cache", False) == True:
            # Current response comes from the cache, no need to update the cache
            return response
        else:
            # used e.g. in unittests
            response._from_cache = False

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
            logger.debug("Don't cache this page (timeout == 0)")
            return response

        # Create a new HttpResponse for the cache, so we can skip existing
        # cookies and attributes like response.csrf_processing_done
        response2 = HttpResponse(
            content=response._container,
            status=200,
            content_type=response['Content-Type'],
        )
        if response.has_header("Content-Language"):
            response2['Content-Language'] = response['Content-Language']
        if settings.DEBUG or settings.RUN_WITH_DEV_SERVER:
            # Check if we store a {% csrf_token %} into the cache
            # This can't work ;)
            for content in response._container:
                if "csrfmiddlewaretoken" in content:
                    raise AssertionError("csrf_token would be put into the cache! content: %r" % content)

        # Adds ETag, Last-Modified, Expires and Cache-Control headers
        patch_response_headers(response2, timeout)

        cache_key = self.get_cache_key(request)
        cache.set(cache_key, response2, timeout)

        logger.debug("Put to cache: %r" % cache_key)
        return response
