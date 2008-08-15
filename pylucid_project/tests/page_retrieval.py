#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    tests.page_fetching
    ~~~~~~~~~~~~~~~~~~~~~~

    Unit tests for page retrieval system.

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import unittest

import tests

from django.contrib.auth.models import User

from PyLucid.models import Page, Template, Style


class PageModel(unittest.TestCase):
    def test_page(self):
        """
        Create a page with a minimum of args.
        If name and shortcut is None, it should be worked, too.
        """
        default_user = User.objects.get(
            username=tests.TEST_USERS["superuser"]["username"]
        )

        default_template = Template.objects.all()[0]
        default_style = Style.objects.all()[0]
        default_markup = 0 # html without TinyMCE

        p = Page(
            name = None,
            shortcut = None,

            template = default_template,
            style = default_style,
            markup = default_markup,
            createby = default_user,
            lastupdateby = default_user,
        )
        p.save()

        self.failUnlessEqual(p.name, "")
        self.failUnlessEqual(p.shortcut, "1")


class getPageByShortcutTestCase(tests.TestCase):
    """
    Unit tests for page shortcut resolving. Tests utilise common test page
    hierarchy.
    """

    def testDefaultPage(self):
        """ No shortcuts in URL. """
        response = self.client.get('/')
         # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)

    def testFullPath(self):
        """ Full path in page request. """
        url = tests.TEST_PAGES_SHORTCUTS[3]
        response = self.client.get(url)
         # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)
        # Check that we got correct page
        self.failUnlessEqual(response.context[0]['PAGE'].shortcut,url.split('/')[-2])

    def testPartialPath(self):
        """ Partial path in page request. """
        url = tests.TEST_PAGES_SHORTCUTS[3]
        url = '/'+'/'.join(url.split('/')[2:])
        response = self.client.get(url)
         # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)
        # Check that we got correct page
        self.failUnlessEqual(response.context[0]['PAGE'].shortcut, url.split('/')[-2])

    def testShortcutOnly(self):
        """ Only shortcut in page request. """
        url = tests.TEST_PAGES_SHORTCUTS[3]
        url = '/'.join(('',url.split('/')[-2],''))
        response = self.client.get(url)
         # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)
        # Check that we got correct page
        self.failUnlessEqual(response.context[0]['PAGE'].shortcut,url.split('/')[-2])

    def testParentMissmatch(self):
        """ Testcase for page which exists under different parent than
        requested. """
        url = u'/1_AAA/2_1_EEE/'
        response = self.client.get(url)
        # Check that the respose is 404 Page Not Found.
        #self.failUnlessEqual(response.status_code, 404)
         # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)
        # Check that we got correct page
        self.failUnlessEqual(response.context[0]['PAGE'].shortcut,url.split('/')[-2])

    def testInvalidShortcutsAtTheEnd(self):
        url = tests.TEST_PAGES_SHORTCUTS[3]+'foo/bar/'
        response = self.client.get(url)
         # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 302)
        # Check that we got correct page
        self.failUnless(response['location'].endswith(tests.TEST_PAGES_SHORTCUTS[3]))



class permitViewPublicTestCase:#(tests.TestCase):
    """
    Unit tests for permitViewPublic handling.
    """
    def setUp(self):
        """
        Create some pages to play with.
        """
        self.publicPage = tests.create_page({'name': 'permitPublicView',
                                             'shortcut': 'permitPublicView'})

        self.loginrequiredPage = tests.create_page({'name': 'disablePublicView',
                                                    'shortcut': 'disablePublicView'})
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

class permitViewGroupTestCase:#(tests.TestCase):
    """
    Unit tests for permitViewGroup handling.
    """
    from django.contrib.auth.models import Group, User

    def setUp(self):
        """
        Create some pages, groups and users to play with.
        """
        # groups
        group_names = ('groupA','groupB')
        groups = {}
        for name in group_names:
            (groups[name],dummy) = self.Group.objects.get_or_create(name=name)
            groups[name].save()
        # users
        USERS = {
            "A": {
                    "username": "userA",
                    "email": "user@example.org",
                    "password": "passwordA",
                    "is_staff": False,
                    "is_superuser": False,
                    },
            "B": {
                    "username": "userB",
                    "email": "user@example.org",
                    "password": "passwordB",
                    "is_staff": False,
                    "is_superuser": False,
                    },
            }
        for usertype, userdata in USERS.iteritems():
            u = tests.create_user(**userdata)
            u.groups.add(groups['group'+usertype])
            u.save
        self.USERS = USERS

        self.groupPage = tests.create_page({'name':'PageForGroupA',"shortcut":"PageForGroupA"})
        self.groupPage.permitViewGroup = groups['groupA']
        self.groupPage.save()

    def testPermViewGroupMember(self):
        """ Group member can see page. """
        self.client.login(username='userA',password=self.USERS['A']['password'])
        url = '/'+self.groupPage.shortcut+'/'
        response = self.client.get(url)
         # Check that the respose is 200 OK.
        self.failUnlessEqual(response.status_code, 200)

    def testPermViewGroupNonMember(self):
        """ Group non-member can't see page. """
        self.client.login(username='userB',password=self.USERS['B']['password'])
        url = '/'+self.groupPage.shortcut+'/'
        response = self.client.get(url)
         # Check that the respose is 302 Redirect and user gets "Access Denied" message.
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(str(self.User.objects.get(username='userB').message_set.all()[0]),
                             'Access denied')

    def testPermViewGroupSuperUser(self):
        """ Superuser can see page. """
        self.login('superuser')
        url = '/'+self.groupPage.shortcut+'/'
        response = self.client.get(url)
         # Check that the respose is 200 OK.
        self.failUnlessEqual(response.status_code, 200)



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
