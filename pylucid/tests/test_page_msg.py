#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test for page_msg

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""
import os
import re
import unittest

import tests
from tests.test_plugin_api import PluginAPI_Base
from tests.utils.FakeRequest import get_fake_context

from django.utils.safestring import mark_safe

from django.conf import settings

from PyLucid.system.page_msg import PageMessages


PAGE_MSG_RE = re.compile("<\/legend>(.*?)<\/fieldset>(?usm)")


class PageMessagesTest(unittest.TestCase):
    """
    Test PyLucid.system.page_msg.PageMessages directly.
    """
    def setUp(self):
        self.fake_context = get_fake_context()
        self.request = self.fake_context["request"]
        self.request.debug = False

        self.page_msg = PageMessages(self.fake_context)

    def test_API(self):
        """
        test the API:
        len(), str(), unicode(), repr(), iter()
        """
        self.assertEqual(len(self.page_msg), 0)
        self.page_msg("first test")
        self.assertEqual(len(self.page_msg), 1)

        self.assertEqual(
            str(self.page_msg),
            'pages messages: <span style="color:blue;">first test</span>'
        )
        self.assertEqual(
            unicode(self.page_msg),
            u'page messages: <span style="color:blue;">first test</span>'
        )
        self.assertEqual(
            repr(self.page_msg),
            'page messages: [u\'<span style="color:blue;">first test</span>\']'
        )
        self.assertEqual(
            repr(self.page_msg),
            'page messages: [u\'<span style="color:blue;">first test</span>\']'
        )


        result = u""
        for line in self.page_msg:
            result += line

        self.assertEqual(
            result,
            u'<span style="color:blue;">first test</span>'
        )

    def test_debug(self):
        self.request.debug = True
        self.page_msg("debug test")
        # In debug mode -> fileinfo should be inserted
        self.failUnless("/tests/test_page_msg.py" not in self.page_msg)

    def test_escape1(self):
        """
        without mark_safe, every string should be escaped
        """
        self.page_msg(u"<1>")
        self.assertEqual(
            unicode(self.page_msg),
            u'page messages: <span style="color:blue;">&lt;1&gt;</span>'
        )
    def test_escape2(self):
        """
        datatypes should be escaped, too.
        """
        self.page_msg({"k": u"<2>"})
        self.failUnless("&lt;2&gt;" not in self.page_msg)

        self.page_msg(["<3>", "<4>"])
        self.failUnless("&lt;3&gt;" not in self.page_msg)
        self.failUnless("&lt;4&gt;" not in self.page_msg)

    def test_make_safe(self):
        """
        A mark_safe string should not be escaped.
        """
        test_string = mark_safe(u"<<<test>>>")
        self.page_msg(test_string)
        self.failUnless(u"<<<test>>>" not in self.page_msg)

    def test_encoding(self):
        """
        Test if the encoding works.
        Encoding of this sourcecode file must be the same as DEFAULT_CHARSET in
        the settings.py file.
        """
        self.page_msg("test äöü")
        self.assertEqual(
            unicode(self.page_msg),
            u'page messages: <span style="color:blue;">test äöü</span>'
        )


class PageMessagesTest2(PluginAPI_Base):
    """
    Test page_msg through the unitest plugin. With the method test_page_msg
    """
    def _get_page_msg(self, url, debug=False):
        raw_content = self._get_plugin_content(url, PAGE_MSG_RE, debug)
        return raw_content

    def test_page_msg(self):
        # FIXME: How to setup these settings?
        settings.DEBUG = False
        settings.INTERNAL_IPS = ()

        url = self.command % "test_page_msg"

        content = self._get_page_msg(url)#, debug=True)
        self.assertEqual2(
            content,
            '<span style="color:blue;">page_msg test:</span><br />\n'
            '\t<span style="color:black;">I am black</span><br />\n'
            '\t<span style="color:red;">RedError!</span><br />\n'
            '\t<span style="color:green;">and green</span><br />'
        )


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
