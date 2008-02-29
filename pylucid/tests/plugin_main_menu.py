#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Tests for  PyLucid.plugins_internal.main_menu

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by Jens Diemer.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, unittest, pprint

import tests

from django.conf import settings

from PyLucid.models import Page, Template, Preference


class TestMainMenu1(tests.TestCase):
    """
    Test the main_menu plugin with all TEST_PAGES
    """
    def setUp(self):
        """
        Create a clean page table.
        """
        Page.objects.all().delete() # Delete all existins pages

        self.template = tests.create_template("{% lucidTag main_menu %}")

        tests.create_pages(tests.TEST_PAGES, template=self.template)

    #__________________________________________________________________________

    def test1(self):
        """
        test all generated links
        """
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


class TestMainMenu2(tests.TestCase):
    """
    Test the main_menu plugin with special pages.
    """
    def setUp(self):
        """
        Create a clean page table.
        """
        Page.objects.all().delete() # Delete all existins pages

        self.template = tests.create_template("{% lucidTag main_menu %}")

    def test_base(self):
        test_pages = [{
            'name': '1_AAA',
            'subitems': [
                {'name': '1_2_BBB'}
            ]
        }]
        tests.create_pages(test_pages, template=self.template)
#        self.create_link_snapshot()
        snapshot = {
            u'/1_AAA/': [('/1_AAA', '1_AAA'), ('/1_AAA/1_2_BBB', '1_2_BBB')],
            u'/1_AAA/1_2_BBB/': [
                ('/1_AAA', '1_AAA'), ('/1_AAA/1_2_BBB', '1_2_BBB')
            ]
        }
        self.link_snapshot_test(snapshot)

    def test_escape_names(self):
        """
        Test with some spezial characters in page names
        """
        test_pages = [{
            'name': '{{ A }} {% B %} <C>',
            'title': '{{ a }} {% b %} <c>',
            'subitems': [
                {'name': '{{ 1 }} {% 2 % } <3>'}
            ]
        }]
        tests.create_pages(test_pages, template=self.template)
#        self.create_link_snapshot()
        snapshot = {
            u'/A-B-C/': [
                ('/A-B-C', '{{ A }} {% B %} &lt;C&gt;'),
                ('/A-B-C/1-2-3', '{{ 1 }} {% 2 % } &lt;3&gt;')
            ],
            u'/A-B-C/1-2-3/': [
                ('/A-B-C', '{{ A }} {% B %} &lt;C&gt;'),
                ('/A-B-C/1-2-3', '{{ 1 }} {% 2 % } &lt;3&gt;')
            ]
        }
        self.link_snapshot_test(snapshot)


if __name__ == "__main__":
    # Run this unitest directly
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])