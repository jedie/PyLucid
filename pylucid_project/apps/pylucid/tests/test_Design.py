#!/usr/bin/env python
# coding: utf-8


"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    TODO: Test colorscheme stuff
    
    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings

from dbpreferences.tests.BrowserDebug import debug_response

from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests.test_tools.scrapping import HTMLscrapper

settings.SERVE_STATIC_FILES = True
#CACHE_DIR = settings.PYLUCID.CACHE_DIR
DEBUG = settings.DEBUG
CACHE_BACKEND = settings.CACHES["default"]["BACKEND"]

COMPRESS_DIR = "/%s/" % getattr(settings, "COMPRESS_OUTPUT_DIR", "CACHE")



class DesignTestCase(basetest.BaseUnittest):
    def setUp(self):
        settings.CACHES["default"]["BACKEND"] = "django.core.cache.backends.locmem.LocMemCache"

    def tearDown(self):
        # Recover changed settings
#        settings.PYLUCID.CACHE_DIR = CACHE_DIR
        settings.CACHES["default"]["BACKEND"] = CACHE_BACKEND

    def get_headlinks(self, response, url_part):
        data = HTMLscrapper().grab(response.content, tags=("link",), attrs=("href",))
#        for url in data["href"]: print url
        return [url for url in data["href"] if url_part in url]

    def get_headfile(self, url, mimetype="text/css"):
        response = self.client.get(url)
        self.assertStatusCode(response, 200)
        self.assertEqual(response["content-type"], mimetype)
        return response.content

    def assertHeadfiles(self, urls):
        for url in urls:
            response = self.client.get(url)
            self.assertStatusCode(response, 200)
            self.assertEqual(response["content-type"], "text/css")



class DesignTest(DesignTestCase):
    def test_cached_headfiles_styles(self):
        response = self.client.get("/")
#        debug_response(response)
        urls = self.get_headlinks(response, COMPRESS_DIR)
        self.assertHeadfiles(urls)

        self.failUnlessEqual(len(urls), 1)

        content = self.get_headfile(urls[0])
        self.failUnless("headfile stylesheet 'initial_site_style/main.css'" in content)
        self.failUnless("headfile stylesheet 'pygments.css'" in content)


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=2)
