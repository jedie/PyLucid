#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    unitest for page_counter plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import re

import tests

from PyLucid.models import Page

# Reex for getting the page count number
COUNT_RE = re.compile("|(\d+?)|")

class PageCounterTest(tests.TestCase):
    """
    Unit tests for page_counter plugin
    """
    def setUp(self):
        test_template = tests.create_template(
            content = "{% lucidTag page_counter %}"
        )
        # Create the test pages defined in content_test_utils.py
        # assign the test template to all pages
        tests.create_pages(tests.TEST_PAGES, template=test_template)

    def test_count(self):
        """
        request every test pages several times and check the page count output
        """
        pages = Page.objects.all()
        self.failIf(len(pages)<3)

        if tests.WORKING_CACHE_BACKEND:
            # With a working cache backend, the counter doesn't work.
            max_tests = 1
        else:
            max_tests = 5

        for page in pages:
            test_url = page.get_absolute_url()
            for test_count in xrange(1,max_tests):
                response = self.client.get(test_url)
                self.failUnlessEqual(response.status_code, 200)

                raw_content = response.content
#                print raw_content
                lines = raw_content.splitlines()
                self.assertEqual(len(lines), 3)
                page_count = int(lines[1])
#                print page_count
                self.assertEqual(page_count, test_count)


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])