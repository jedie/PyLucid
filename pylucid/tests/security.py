#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test for cross-site scripting and SQL injections.

    A XSS atac needs to inject a html tag who must start with "<". We test all
    encoding variantes of the character in combinaltion with a test string. We
    check in every response content the existing.

    Some tests need a long time. We print additional "alive" point out ;)

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys

import tests
from tests.utils.BrowserDebug import debug_response

from django.conf import settings

from PyLucid.models import Page

# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True

CHARACTER_VARIANTS = (
    "<", r"\x3c", r"\x3C", r"\u003c", u"\u003c", u"\u003C",
#    "&#60", "&#060", "&#0060", "&#00060", "&#000060", "&#0000060", "&#60;",
#    "&#060;", "&#0060;", "&#00060;", "&#000060;", "&#0000060;",
#    "&#x3c", "&#x03c", "&#x003c", "&#x0003c", "&#x00003c", "&#x000003c",
#    "&#x3c;", "&#x03c;", "&#x003c;", "&#x0003c;", "&#x00003c;", "&#x000003c;",
#    "&#X3c", "&#X03c", "&#X003c", "&#X0003c", "&#X00003c", "&#X000003c",
#    "&#X3c;", "&#X03c;", "&#X003c;", "&#X0003c;", "&#X00003c;", "&#X000003c;",
#    "&#x3C", "&#x03C", "&#x003C", "&#x0003C", "&#x00003C", "&#x000003C",
#    "&#x3C;", "&#x03C;", "&#x003C;", "&#x0003C;", "&#x00003C;", "&#x000003C;",
#    "&#X3C", "&#X03C", "&#X003C", "&#X0003C", "&#X00003C", "&#X000003C",
#    "&#X3C;", "&#X03C;", "&#X003C;", "&#X0003C;", "&#X00003C;", "&#X000003C;",
)
VARIANTS_STRING = "XSS_TEST"

PAGE_ID = 1

POST_URLS = (
    # search plugin
    (
        "/search/do_search/",
        {"search_string": []},
    ),
    # auth login - submit username
    (
        "/auth/login/",
        {
            'username': ['test'],
            'sha_login': ['SHA-1 login'],
            'next_url': ['']
        },
    ),
    # auth login - submit password
    (
        "/auth/login/",
        {
            u'username': [u'test'],
            u'sha_login': [u'little secure sha login'],
            u'sha_a2': [u'd0cf6828278e6f016b71827c884a82fc7f5b1204'],
            u'sha_b': [u'87c7a6a5ff0225ce7a99'],
            u'next_url': [u'']
        },
    ),
)
GET_URLS = (
    "/RSSfeedGenerator/download/RSS.xml?count=%s",
    "/page_style/sendStyle/%s.css",
)

SQL_INJECTIONS = (
#    "DROP TABLE PyLucid_page;",
#    "; DROP TABLE PyLucid_page;",

    '"DROP TABLE PyLucid_page;"',
    '"; DROP TABLE PyLucid_page;"',
    "'DROP TABLE PyLucid_page;'",
    "'; DROP TABLE PyLucid_page;'",

#    '\"DROP TABLE PyLucid_page;\"',
#    '\"; DROP TABLE PyLucid_page;\"',
#    "\'DROP TABLE PyLucid_page;\'",
#    "\'; DROP TABLE PyLucid_page;\'",
#
#    # SEMICOLON
#    "\x3B DROP TABLE PyLucid_page\x3B",
#    u"\u003B DROP TABLE PyLucid_page\u003B",
#
#    # QUOTATION MARK
#    "\x22DROP TABLE PyLucid_page;\x22",
#    "\x22; DROP TABLE PyLucid_page;\x22",
#    u"\u0022DROP TABLE PyLucid_page;\u0022",
#    u"\u0022; DROP TABLE PyLucid_page;\u0022",
#
#    # APOSTROPHE
#    "\x27DROP TABLE PyLucid_page;\x27",
#    "\x27; DROP TABLE PyLucid_page;\x27",
#    u"\u0027DROP TABLE PyLucid_page;\u0027",
#    u"\u0027; DROP TABLE PyLucid_page;\u0027",
#
#    # GRAVE ACCENT
#    "\x60DROP TABLE PyLucid_page;\x60",
#    "\x60; DROP TABLE PyLucid_page;\x60",
#    u"\u0060DROP TABLE PyLucid_page;\u0060",
#    u"\u0060; DROP TABLE PyLucid_page;\u0060",
)


class TestBase(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    def setUp(self):
        settings.DEBUG=False

        self.base_url = "/%s/%s" % (settings.COMMAND_URL_PREFIX, PAGE_ID)


class TestXSS(TestBase):
    """
    cross-site scripting test
    """
    def test_page_request(self):
        """
        normal page request with all "<"-combinations.
        """
        for char_variant in CHARACTER_VARIANTS:
            test_string = char_variant + VARIANTS_STRING
            url = "/" + test_string
            response = self.client.get(url)
            self.assertResponse(
                response, must_not_contain=(test_string, "<" + VARIANTS_STRING,)
            )

    def test_post(self):
        """
        Test all POST_URLS.
        We replace all POST values individually with all "<"-combinations.
        """
        for url, init_post_data in POST_URLS:
            test_url = self.base_url + url

            for key, value in init_post_data.iteritems():
                sys.stdout.write(".")
                post_data = init_post_data.copy()

                for char_variant in CHARACTER_VARIANTS:
                    test_string = char_variant + VARIANTS_STRING
                    post_data[key] = test_string

                    response = self.client.post(test_url, post_data)
                    self.assertResponse(
                        response,
                        must_not_contain=("<" + VARIANTS_STRING,)
                    )

    def test_get(self):
        """
        Test GET_URLS with all "<"-combinations.
        """
        for url in GET_URLS:
            sys.stdout.write(".")

            for char_variant in CHARACTER_VARIANTS:
                test_string = char_variant + VARIANTS_STRING
                test_url = self.base_url + url % test_string

                response = self.client.get(test_url)
                self.assertResponse(
                    response,
                    must_not_contain=("<" + VARIANTS_STRING,)
                )


class TestSQLinjections(TestBase):
    """
    SQL injections test
    """
    def test_page_request(self):
        """
        normal page request with all "<"-combinations.
        """
        for sql_statement in SQL_INJECTIONS:
            url = "/" + sql_statement
            response = self.client.get(url)
            assert Page.objects.count()>0

            url = url.replace(" ", "+")
            response = self.client.get(url)
            assert Page.objects.count()>0


    def test_post(self):
        """
        Test all POST_URLS.
        We replace all POST values individually with all SQL_INJECTIONS strings.
        """
        for url, init_post_data in POST_URLS:
            test_url = self.base_url + url

            for key, value in init_post_data.iteritems():
                sys.stdout.write(".")
                post_data = init_post_data.copy()

                for sql_statement in SQL_INJECTIONS:
                    post_data[key] = sql_statement

                    response = self.client.post(test_url, post_data)
                    assert Page.objects.count()>0


    def test_get(self):
        """
        Test GET_URLS with all SQL_INJECTIONS strings.
        """
        for url in GET_URLS:
            sys.stdout.write(".")

            for sql_statement in SQL_INJECTIONS:
                test_url = self.base_url + url % sql_statement

                response = self.client.get(test_url)
                assert Page.objects.count()>0

                test_url = test_url.replace(" ", "+")
                response = self.client.get(test_url)
                assert Page.objects.count()>0



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])