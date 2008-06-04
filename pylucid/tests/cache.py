#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the PyLucid page cache middleware.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os

import tests
from tests.utils.BrowserDebug import debug_response

from django.conf import settings
from django.http import HttpResponse
from django.core.cache import cache

from PyLucid.models import Page, Template, Style

# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True

PAGE_CONTENT_PREFIX = "page content:"

CACHE_CONTENT = "Cached content!"

SHORTCUT = "CacheTestPage"

CACHE_KEY_PREFIX = settings.PAGE_CACHE_PREFIX + SHORTCUT

class TestCache(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    #--------------------------------------------------------------------------

    @tests.requires_cache
    def setUp(self):
        settings.DEBUG=True

        Page.objects.all().delete() # Delete all existins pages

        self.template = tests.create_template(
            name = "cache test template",
            content = (
                "{{ PAGE.content }}\n"
                "{{ PAGE.get_permalink }}\n"
                "<!-- script_duration -->"
            ),
        )

        def get_page_dict(no):
            page = {
                "name": SHORTCUT + no,
                "shortcut": SHORTCUT + no,
                "content": PAGE_CONTENT_PREFIX + no,
                "template": self.template,
            }
            return page

        test_pages = [get_page_dict("1"), get_page_dict("2")]
        tests.create_pages(test_pages, template=self.template)
        #self.create_link_snapshot()

        self._prepare_cache()

    def _prepare_cache(self):
        """
        -delete the first test page, if exist in the cache.
        -Add the second test page into the cache.
        """
        cache.delete(CACHE_KEY_PREFIX + "1")
        response = HttpResponse(CACHE_CONTENT + "<!-- script_duration -->")
        cache.set(CACHE_KEY_PREFIX + "2", response, 9999)

    #--------------------------------------------------------------------------

    def failIfFromCache(self, response, msg=None):
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(PAGE_CONTENT_PREFIX, "render time", "queries"),
            must_not_contain=("Traceback",)
        )
        self.failUnlessEqual(response["from_cache"], "no", msg)

    def failIfNotFromCache(self, response, msg=None):
        self.failUnlessEqual(response.status_code, 200)
        url = response.request["PATH_INFO"]
        if url == "/%s1" % SHORTCUT:
            self.assertResponse(
                response,
                must_contain=(PAGE_CONTENT_PREFIX, "render time", "queries"),
                must_not_contain=(CACHE_CONTENT, "Traceback",)
            )
        elif url == "/%s2" % SHORTCUT:
            self.assertResponse(
                response,
                must_contain=(CACHE_CONTENT, "render time", "queries"),
                must_not_contain=(PAGE_CONTENT_PREFIX, "Traceback",)
            )
        else:
            raise AssertionError("Wrong url?")

        self.failUnlessEqual(response["from_cache"], "yes", msg)

    #--------------------------------------------------------------------------

    @tests.requires_cache
    def test_prepage(self):
        """
        Test the test environment ;)
        """
        # Test _prepare_cache()
        self.failUnlessEqual(cache.get(CACHE_KEY_PREFIX + "1"), None)
        response = cache.get(CACHE_KEY_PREFIX + "2")
        self.failUnlessEqual(
            response.content, CACHE_CONTENT + "<!-- script_duration -->"
        )

        # Check if the test pages exist
        snapshot = {u'/CacheTestPage1/': [], u'/CacheTestPage2/': []}
        self.link_snapshot_test(snapshot)

        # Request the first test page
        response = self.client.get("/%s1" % SHORTCUT)
        #debug_response(response)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(PAGE_CONTENT_PREFIX, "render time", "queries"),
            must_not_contain=("Traceback",)
        )

    @tests.requires_cache
    def test_assertion(self):
        """
        The cache middleware should only use the cached response, if it's a
        django HttpResponse instance otherwise it sould raise a AssertionError.
        """
        cache.set(
            CACHE_KEY_PREFIX + "3",
            "a string and not a django HttpResponse instance!",
            9999
        )
        url = "/%s3" % SHORTCUT
        self.assertRaises(AssertionError, self.client.get, url)

    @tests.requires_cache
    def test_cache(self):
        """
        Check if the second test page comes from the cache.
        """
        url = "/%s2" % SHORTCUT
        response = self.client.get(url)
        self.assertResponse(
            response,
            must_contain=(CACHE_CONTENT,),
            must_not_contain=(PAGE_CONTENT_PREFIX,)
        )

    #--------------------------------------------------------------------------

    @tests.requires_cache
    def test_get(self):
        """
        Test the cache with normal GET request.
        """
        for i in xrange(3):
            url = "/%s1" % SHORTCUT

            # First request -> can't exist in the cache
            response = self.client.get(url)
            self.failIfFromCache(response, "loop: %s" % i)

            # Second request must comes from the cache
            response = self.client.get(url)
            self.failIfNotFromCache(response, "loop: %s" % i)

            # Delete the test page from the cache
            cache.delete(CACHE_KEY_PREFIX + "1")


    @tests.requires_cache
    def test_post(self):
        """
        POST request should never use the cache.
        """
        # But a POST request should never use the cache
        url = "/%s2" % SHORTCUT
        response = self.client.post(url)
        self.failIfFromCache(response)

    #--------------------------------------------------------------------------

    def _check_cache_after(self, func):
        # The secont test page must now comes from the cache
        url = "/%s2" % SHORTCUT
        response = self.client.get(url)
        self.failIfNotFromCache(response)

        # execute the given function
        func()

        # After edit, the cache should be deleted.
        response = cache.get(CACHE_KEY_PREFIX + "2")
        self.failUnlessEqual(response, None)

        # Check the GET response, too.
        response = self.client.get(url)
        self.failIfFromCache(response)


    @tests.requires_cache
    def test_page_edit(self):
        """
        After a page content has been edited, the cache variante must be
        deleted.
        """
        def test_func():
            """ 'edit' a page """
            page = Page.objects.get(shortcut__exact=SHORTCUT + "2")
            page.content = PAGE_CONTENT_PREFIX + "new content!"
            page.save()

        self._check_cache_after(test_func)

    @tests.requires_cache
    def test_template_edit(self):
        """
        If a template has been changes, the cache should be deleted.
        """
        def test_func():
            """ 'edit' a template """
            template = Template.objects.all()[0]
            template.save()

        self._check_cache_after(test_func)

    @tests.requires_cache
    def test_styleheet_edit(self):
        """
        If a styleheet has been changes, the cache should be deleted.
        """
        def test_func():
            """ 'edit' a styleheet """
            styleheet = Style.objects.all()[0]
            styleheet.save()

        self._check_cache_after(test_func)

    #--------------------------------------------------------------------------

    @tests.requires_cache
    def test_wrong_url(self):
        """
        Test if the cache middleware checks bad characters in the url.
        Normaly the urls-re doesn't match on bad urls. But the process_request
        method of a middleware called before this.
        """
        content = "Should never comes from the cache!"
        shortcut = "bad$char&here"
        url = "/%s/" % shortcut
        cache_key = settings.PAGE_CACHE_PREFIX + shortcut

        # Insert a cache entry, so the cache middleware can found the cached
        # page and will be response the cached content, if the shortcut will
        # not be veryfied.
        response = HttpResponse(content)
        cache.set(cache_key, response, 9999)

        # Request the cached page and check the response. It should not resonse
        # the cached content. It should be apperar a 404 page not found.
        response = self.client.get(url)
        #debug_response(response)
        self.failUnlessEqual(response.status_code, 404)
        self.assertResponse(response, must_not_contain=(content,))


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
