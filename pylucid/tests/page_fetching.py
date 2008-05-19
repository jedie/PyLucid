#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    tests.page_fetching
    ~~~~~~~~~~~~~~~~~~~~~~

    Unit tests for page retrieval system.

    :copyleft: Perttu Ranta-aho
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import tests


class detectPageTestCase(tests.TestCase):
    """
    Unit tests for detect_page function.
    """

    def testParentMissmatch(self):
        """ Testcase for page which exists under different parent than
        requested. Test utilises common test page hierarchy."""
        
        url = tests.TEST_PAGES_SHORTCUTS[1]
        response = self.client.get(url)
         # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)
        
        url = u'/1_AAA/2_1_EEE/'
        response = self.client.get(url)
        print response
        # Check that the respose is 404 Page Not Found.
        self.failUnlessEqual(response.status_code, 404)
