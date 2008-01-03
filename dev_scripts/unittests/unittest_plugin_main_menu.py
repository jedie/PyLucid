#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test PyLucid.plugins_internal.back_links
    Tests the arguments of the plugin tag

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from setup_environment import setup#, get_fake_context
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=True,
    install_plugins=True
)

#______________________________________________________________________________
# Test:

import os, unittest, pprint

from django.conf import settings
from django.test.client import Client

from content_tests_utils import ContentTestBase, TEST_PAGES
from PyLucid.db.internal_pages import get_internal_page
from PyLucid.models import Page, Template, Preference


# vebose test?
DEBUG = True
#DEBUG = False


PLUGIN_NAME = "main_menu"
INTERNAL_PAGE_NAME = "menu_item"




class TestPrepare(ContentTestBase):
    """
    Test the href regex
    """
    def test_href_re(self):
        """
        Get all links from the internal page and compare with a reference.
        """
        internal_page = get_internal_page(PLUGIN_NAME, INTERNAL_PAGE_NAME)
        content = internal_page.content_html

        links = self.get_links(content)
#        print links
        self.assertEqual(links, [(u'{{ href }}', u'{{ name }}')])




class TestBase(ContentTestBase):
    """
    Test the backlinks plugin.
    """
    def setUp(self):
        """
        Create a clean page table.
        """
        Page.objects.all().delete() # Delete all existins pages

        self.template = self.create_template("{% lucidTag main_menu %}")

        # Create the test pages defined in content_test_utils.py
        # assign the test template to all pages
        self.create_pages(TEST_PAGES, template=self.template)

    #__________________________________________________________________________

    def test1(self):
        """
        test all generated links
        """
#        self.create_link_snapshot()
        snapshot = {u'/1_AAA/': [('/1_AAA', '1_AAA'),
                      ('/1_AAA/1_1_BBB', '1_1_BBB'),
                      ('/1_AAA/1_2_BBB', '1_2_BBB'),
                      ('/2_DDD', '2_DDD')],
         u'/1_AAA/1_1_BBB/': [('/1_AAA', '1_AAA'),
                              ('/1_AAA/1_1_BBB', '1_1_BBB'),
                              ('/1_AAA/1_2_BBB', '1_2_BBB'),
                              ('/2_DDD', '2_DDD')],
         u'/1_AAA/1_2_BBB/': [('/1_AAA', '1_AAA'),
                              ('/1_AAA/1_1_BBB', '1_1_BBB'),
                              ('/1_AAA/1_2_BBB', '1_2_BBB'),
                              ('/1_AAA/1_2_BBB/1_2_1_CCC', '1_2_1_CCC'),
                              ('/1_AAA/1_2_BBB/1_2_2_CCC', '1_2_2_CCC'),
                              ('/2_DDD', '2_DDD')],
         u'/1_AAA/1_2_BBB/1_2_1_CCC/': [('/1_AAA', '1_AAA'),
                                        ('/1_AAA/1_1_BBB', '1_1_BBB'),
                                        ('/1_AAA/1_2_BBB', '1_2_BBB'),
                                        ('/1_AAA/1_2_BBB/1_2_1_CCC', '1_2_1_CCC'),
                                        ('/1_AAA/1_2_BBB/1_2_2_CCC', '1_2_2_CCC'),
                                        ('/2_DDD', '2_DDD')],
         u'/1_AAA/1_2_BBB/1_2_2_CCC/': [('/1_AAA', '1_AAA'),
                                        ('/1_AAA/1_1_BBB', '1_1_BBB'),
                                        ('/1_AAA/1_2_BBB', '1_2_BBB'),
                                        ('/1_AAA/1_2_BBB/1_2_1_CCC', '1_2_1_CCC'),
                                        ('/1_AAA/1_2_BBB/1_2_2_CCC', '1_2_2_CCC'),
                                        ('/2_DDD', '2_DDD')],
         u'/2_DDD/': [('/1_AAA', '1_AAA'),
                      ('/2_DDD', '2_DDD'),
                      ('/2_DDD/2_1_EEE', '2_1_EEE'),
                      ('/2_DDD/2_2_EEE', '2_2_EEE')],
         u'/2_DDD/2_1_EEE/': [('/1_AAA', '1_AAA'),
                              ('/2_DDD', '2_DDD'),
                              ('/2_DDD/2_1_EEE', '2_1_EEE'),
                              ('/2_DDD/2_2_EEE', '2_2_EEE')],
         u'/2_DDD/2_2_EEE/': [('/1_AAA', '1_AAA'),
                              ('/2_DDD', '2_DDD'),
                              ('/2_DDD/2_1_EEE', '2_1_EEE'),
                              ('/2_DDD/2_2_EEE', '2_2_EEE')]}
        self.link_snapshot_test(snapshot)



if __name__ == "__main__":
    print
    print ">>> Unitest: PyLucid.plugins_internal.back_links"
    print
    print "_"*79
    unittest.main()
