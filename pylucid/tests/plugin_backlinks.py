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

from PyLucid.models import Page, Template, Preference


class TestBase(tests.TestCase):
    """
    Test the backlinks plugin.
    """
    def setUp(self):
        """
        Create a clean page table.
        """
        Page.objects.all().delete() # Delete all existins pages

        self.template = tests.create_template("{% lucidTag back_links %}")

        # Create the test pages defined in content_test_utils.py
        # assign the test template to all pages
        tests.create_pages(tests.TEST_PAGES, template=self.template)

    #__________________________________________________________________________

    def test_no_arguments(self):
        """
        test with the default template with no arguments
        print_last_page=False, print_index=False, index="Index"
        """

#        self.create_link_snapshot()
        snapshot = {
            u'/1_AAA/': [],
            u'/1_AAA/1_1_BBB/': [('/1_AAA/', '1_AAA')],
            u'/1_AAA/1_2_BBB/': [('/1_AAA/', '1_AAA')],
            u'/1_AAA/1_2_BBB/1_2_1_CCC/': [('/1_AAA/', '1_AAA'),
                                           ('/1_AAA/1_2_BBB/', '1_2_BBB')],
            u'/1_AAA/1_2_BBB/1_2_2_CCC/': [('/1_AAA/', '1_AAA'),
                                           ('/1_AAA/1_2_BBB/', '1_2_BBB')],
            u'/2_DDD/': [],
            u'/2_DDD/2_1_EEE/': [('/2_DDD/', '2_DDD')],
            u'/2_DDD/2_2_EEE/': [('/2_DDD/', '2_DDD')]
        }
        self.link_snapshot_test(snapshot)

    def test_print_last_page(self):
        """
        print_last_page="True"
        """

        self.template.content = (
            '{% lucidTag back_links print_last_page="True" %}'
        )
        self.template.save()

#        self.create_link_snapshot()
        snapshot = {
         u'/1_AAA/': [('/1_AAA/', '1_AAA')],
         u'/1_AAA/1_1_BBB/': [('/1_AAA/', '1_AAA'), ('/1_AAA/1_1_BBB/', '1_1_BBB')],
         u'/1_AAA/1_2_BBB/': [('/1_AAA/', '1_AAA'), ('/1_AAA/1_2_BBB/', '1_2_BBB')],
         u'/1_AAA/1_2_BBB/1_2_1_CCC/': [('/1_AAA/', '1_AAA'),
                                        ('/1_AAA/1_2_BBB/', '1_2_BBB'),
                                        ('/1_AAA/1_2_BBB/1_2_1_CCC/', '1_2_1_CCC')],
         u'/1_AAA/1_2_BBB/1_2_2_CCC/': [('/1_AAA/', '1_AAA'),
                                        ('/1_AAA/1_2_BBB/', '1_2_BBB'),
                                        ('/1_AAA/1_2_BBB/1_2_2_CCC/', '1_2_2_CCC')],
         u'/2_DDD/': [('/2_DDD/', '2_DDD')],
         u'/2_DDD/2_1_EEE/': [('/2_DDD/', '2_DDD'), ('/2_DDD/2_1_EEE/', '2_1_EEE')],
         u'/2_DDD/2_2_EEE/': [('/2_DDD/', '2_DDD'), ('/2_DDD/2_2_EEE/', '2_2_EEE')]
        }
        self.link_snapshot_test(snapshot)

    def test_print_index1(self):
        """
        print_index="True"
        """

        self.template.content = (
            '{% lucidTag back_links print_index="True" %}'
        )
        self.template.save()

#        self.create_link_snapshot()
        snapshot ={
         u'/1_AAA/': [],
         u'/1_AAA/1_1_BBB/': [('/', 'Index'), ('/1_AAA/', '1_AAA')],
         u'/1_AAA/1_2_BBB/': [('/', 'Index'), ('/1_AAA/', '1_AAA')],
         u'/1_AAA/1_2_BBB/1_2_1_CCC/': [('/', 'Index'),
                                        ('/1_AAA/', '1_AAA'),
                                        ('/1_AAA/1_2_BBB/', '1_2_BBB')],
         u'/1_AAA/1_2_BBB/1_2_2_CCC/': [('/', 'Index'),
                                        ('/1_AAA/', '1_AAA'),
                                        ('/1_AAA/1_2_BBB/', '1_2_BBB')],
         u'/2_DDD/': [],
         u'/2_DDD/2_1_EEE/': [('/', 'Index'), ('/2_DDD/', '2_DDD')],
         u'/2_DDD/2_2_EEE/': [('/', 'Index'), ('/2_DDD/', '2_DDD')]
        }
        self.link_snapshot_test(snapshot)

    def test_print_index2(self):
        """
        print_index="True" index="|"
        """

        self.template.content = (
            '{% lucidTag back_links print_index="True" index="|" %}'
        )
        self.template.save()

#        self.create_link_snapshot()
        snapshot ={
         u'/1_AAA/': [],
         u'/1_AAA/1_1_BBB/': [('/', '|'), ('/1_AAA/', '1_AAA')],
         u'/1_AAA/1_2_BBB/': [('/', '|'), ('/1_AAA/', '1_AAA')],
         u'/1_AAA/1_2_BBB/1_2_1_CCC/': [('/', '|'),
                                        ('/1_AAA/', '1_AAA'),
                                        ('/1_AAA/1_2_BBB/', '1_2_BBB')],
         u'/1_AAA/1_2_BBB/1_2_2_CCC/': [('/', '|'),
                                        ('/1_AAA/', '1_AAA'),
                                        ('/1_AAA/1_2_BBB/', '1_2_BBB')],
         u'/2_DDD/': [],
         u'/2_DDD/2_1_EEE/': [('/', '|'), ('/2_DDD/', '2_DDD')],
         u'/2_DDD/2_2_EEE/': [('/', '|'), ('/2_DDD/', '2_DDD')]
        }
        self.link_snapshot_test(snapshot)


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])