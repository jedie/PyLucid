#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test PyLucid.plugins_internal.back_links
    Tests the arguments of the plugin tag

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by Jens Diemer.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

#______________________________________________________________________________
# Test:

import os, pprint

import tests

from django.conf import settings

from PyLucid.models import Page, Template


class TestBase(tests.TestCase):
    """
    Test the backlinks plugin with snapshot function.
    """
    def setUp(self):
        """
        Create a clean page table.
        """
        Page.objects.all().delete() # Delete all existins pages

        self.template = tests.create_template(
            content = "{% lucidTag back_links %}"
        )

        # Create the test pages defined in content_test_utils.py
        # assign the test template to all pages
        tests.create_pages(tests.TEST_PAGES, template=self.template)

    #__________________________________________________________________________

    def test_1(self):
        """
        print_last_page=False
        print_index=False
        """
        tests.change_preferences(
            plugin_name = "back_links",
            print_last_page=False,
            print_index=False, index_url="URL", index="TITLE"
        )
        #self.create_link_snapshot()
        snapshot = {u'/1_AAA/': [],
             u'/1_AAA/1_1_BBB/': [('/1_AAA/', '1_AAA')],
             u'/1_AAA/1_2_BBB/': [('/1_AAA/', '1_AAA')],
             u'/1_AAA/1_2_BBB/1_2_1_CCC/': [('/1_AAA/', '1_AAA'),
                                            ('/1_AAA/1_2_BBB/', '1_2_BBB')],
             u'/1_AAA/1_2_BBB/1_2_2_CCC/': [('/1_AAA/', '1_AAA'),
                                            ('/1_AAA/1_2_BBB/', '1_2_BBB')],
             u'/2_DDD/': [],
             u'/2_DDD/2_1_EEE/': [('/2_DDD/', '2_DDD')],
             u'/2_DDD/2_2_EEE/': [('/2_DDD/', '2_DDD')]}
        self.link_snapshot_test(snapshot)


    def test_2(self):
        """
        print_last_page=False
        print_index=True
        """
        tests.change_preferences(
            plugin_name = "back_links",
            print_last_page=False,
            print_index=True, index_url="URL", index="TITLE"
        )
        #self.create_link_snapshot()
        snapshot = {u'/1_AAA/': [],
             u'/1_AAA/1_1_BBB/': [('URL', 'TITLE'), ('/1_AAA/', '1_AAA')],
             u'/1_AAA/1_2_BBB/': [('URL', 'TITLE'), ('/1_AAA/', '1_AAA')],
             u'/1_AAA/1_2_BBB/1_2_1_CCC/': [('URL', 'TITLE'),
                                            ('/1_AAA/', '1_AAA'),
                                            ('/1_AAA/1_2_BBB/', '1_2_BBB')],
             u'/1_AAA/1_2_BBB/1_2_2_CCC/': [('URL', 'TITLE'),
                                            ('/1_AAA/', '1_AAA'),
                                            ('/1_AAA/1_2_BBB/', '1_2_BBB')],
             u'/2_DDD/': [],
             u'/2_DDD/2_1_EEE/': [('URL', 'TITLE'), ('/2_DDD/', '2_DDD')],
             u'/2_DDD/2_2_EEE/': [('URL', 'TITLE'), ('/2_DDD/', '2_DDD')]}
        self.link_snapshot_test(snapshot)


    def test_3(self):
        """
        print_last_page=True
        print_index=True
        """
        tests.change_preferences(
            plugin_name = "back_links",
            print_last_page=True,
            print_index=True, index_url="URL", index="TITLE"
        )
        #self.create_link_snapshot()
        snapshot = {u'/1_AAA/': [('URL', 'TITLE'), ('/1_AAA/', '1_AAA')],
             u'/1_AAA/1_1_BBB/': [('URL', 'TITLE'),
                                  ('/1_AAA/', '1_AAA'),
                                  ('/1_AAA/1_1_BBB/', '1_1_BBB')],
             u'/1_AAA/1_2_BBB/': [('URL', 'TITLE'),
                                  ('/1_AAA/', '1_AAA'),
                                  ('/1_AAA/1_2_BBB/', '1_2_BBB')],
             u'/1_AAA/1_2_BBB/1_2_1_CCC/': [('URL', 'TITLE'),
                                            ('/1_AAA/', '1_AAA'),
                                            ('/1_AAA/1_2_BBB/', '1_2_BBB'),
                                            ('/1_AAA/1_2_BBB/1_2_1_CCC/', '1_2_1_CCC')],
             u'/1_AAA/1_2_BBB/1_2_2_CCC/': [('URL', 'TITLE'),
                                            ('/1_AAA/', '1_AAA'),
                                            ('/1_AAA/1_2_BBB/', '1_2_BBB'),
                                            ('/1_AAA/1_2_BBB/1_2_2_CCC/', '1_2_2_CCC')],
             u'/2_DDD/': [('URL', 'TITLE'), ('/2_DDD/', '2_DDD')],
             u'/2_DDD/2_1_EEE/': [('URL', 'TITLE'),
                                  ('/2_DDD/', '2_DDD'),
                                  ('/2_DDD/2_1_EEE/', '2_1_EEE')],
             u'/2_DDD/2_2_EEE/': [('URL', 'TITLE'),
                                  ('/2_DDD/', '2_DDD'),
                                  ('/2_DDD/2_2_EEE/', '2_2_EEE')]}
        self.link_snapshot_test(snapshot)



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
