#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    TODO: Test colorscheme stuff
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings

from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests.test_tools.scrapping import HTMLscrapper


CACHE_DIR = settings.PYLUCID.CACHE_DIR
DEBUG = settings.DEBUG
CACHE_BACKEND = settings.CACHE_BACKEND


class DesignTestCase(basetest.BaseUnittest):
    def setUp(self):
        settings.CACHE_BACKEND = "dummy://"

    def tearDown(self):
        # Recover changed settings
        settings.PYLUCID.CACHE_DIR = CACHE_DIR
        settings.CACHE_BACKEND = CACHE_BACKEND

    def get_headlinks(self, response):
        data = HTMLscrapper().grab(response.content, tags=("link",), attrs=("href",))
        return [url for url in data["href"] if "headfile" in url]

    def assertHeadfiles(self, urls):
        for url in urls:
            response = self.client.get(url)
            self.assertStatusCode(response, 200)
            self.assertEqual(response["content-type"], "text/css")



class DesignTest(DesignTestCase):
    def test_cached_headfiles_styles(self):
        self.assertTrue(settings.PYLUCID.CACHE_DIR != "")

        url_part = "/%s/" % settings.PYLUCID.CACHE_DIR

        response = self.client.get("/")
        urls = self.get_headlinks(response)
        self.assertTrue(len(urls) == 2)
        self.assertHeadfiles(urls)
        for url in urls:
            self.assertTrue(
                url_part in url,
                "url doesn't contain %r: %r" % (url_part, url)
            )

    def test_send_view(self):
        settings.PYLUCID.CACHE_DIR = ""

        prefix = "/%s/" % settings.PYLUCID.HEAD_FILES_URL_PREFIX

        response = self.client.get("/en/")
        urls = self.get_headlinks(response)
        self.assertTrue(len(urls) == 2)
        self.assertHeadfiles(urls)
        for url in urls:
            self.assertTrue(
                url.startswith(prefix),
                "url doesn't starts with %r: %r" % (prefix, url)
            )



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=2)
