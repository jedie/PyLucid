#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    tests.page_permissions
    ~~~~~~~~~~~~~~~~~~~~~~

    Unit tests for page permission system.

    :copyleft: Perttu Ranta-aho
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import tests


class permitViewPublicTestCase(tests.TestCase):
    """
    Unit tests for permitViewPublic handling.
    """
    def setUp(self):
        """
        Create some pages to play with.
        """
        self.publicPage = tests.create_page({'name':'permitPublicView'})

        self.loginrequiredPage = tests.create_page({'name':'disablePublicView'})
        self.loginrequiredPage.permitViewPublic = False
        self.loginrequiredPage.save()

    def testPermViewPublicGranted(self):
        """ Anonymous can see pages by default. """
        url = '/'+self.publicPage.shortcut+'/'
        response = self.client.get(url)
         # Check that the respose is 200 OK.
        self.failUnlessEqual(response.status_code, 200)

    def testPermViewPublicFalse(self):
        """ Setting permitViewPublic false denies anonymous access and
        redirects to login page with next_url set to requested page."""
        url = '/'+self.loginrequiredPage.shortcut+'/'
        response = self.client.get(url)
        # Check that the respose is 302 Moved temporarily.
        self.failUnlessEqual(response.status_code, 302)
        # Check that redirect includes link back to requested page
        self.failUnless(response['location'].endswith('?next='+url))

    def testPermViewPublicLoggedInUser(self):
        """ Logged in user can see page regardless of permitPublicView value. """
        # login with the "normal" test user
        self.login("normal")

         # Check that the respose is for both pages 200 OK.
        url = '/'+self.loginrequiredPage.shortcut+'/'
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        url = '/'+self.publicPage.shortcut+'/'
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])