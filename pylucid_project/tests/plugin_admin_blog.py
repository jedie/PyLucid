#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test PyLucid.plugins_internal.blog

    TODO:
        -Test anonymous functions
        -Test antispam parts
        -Test mail notify
        -...

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: 1781 $
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

#______________________________________________________________________________
# Test:

import tests

from django.conf import settings

from PyLucid.models import Page

ONE_BROWSER_TRACEBACK = True

# Run test with:
PAGE_ID = 1

class TestPluginBlog(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []
   
    def __init__(self, *args, **kwargs):
        super(TestPluginBlog, self).__init__(*args, **kwargs)

        self.base_url = "/%s/%s/blog/" % (
            settings.COMMAND_URL_PREFIX, PAGE_ID
        )
        self.add_entry_url = self.base_url + "add_entry/"
        self.detail_url = self.base_url + "detail/1/"

    def setUp(self):
        """
        Create a clean page table.
        """
        Page.objects.all().delete() # Delete all existins pages

        # Create one page
        self.test_page = tests.create_page(
            name = "blog",
            shortcut = "blog",
            content = "{% lucidTag blog %}",
        )
        
    def test_index(self):
        """
        get the blog page.
        """
        response = self.client.get("/blog/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("blog - all entries","tag cloud", "syndication feeds"),
            must_not_contain=("Traceback", "Error",),
        )

    def test_create_entry(self):
        """
        TODO: Test with 'normal' user ? 
        """
        # Login as a 'staff' user
        self.login("staff")
        response = self.client.get("/blog/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("blog", "tag cloud", "create a new blog entry"),
            must_not_contain=("Traceback", "Error",),
        )
        
    def test_create_form(self):
        """
        Get the form for adding a new blog entry
        """
        self.login("staff")
        response = self.client.get(self.add_entry_url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("blog", "Create a new blog entry", "save"),
            must_not_contain=("Traceback", "Error",),
        )
        
    def test_create_new_blog_entry(self):
        """
        as staff user:
        1. create a new blog entry
        2. Leave a comment 
        """
        self.login("staff")
         
        # Create a new blog entry
        response = self.client.post(
            self.add_entry_url,
            {
                u'headline': u'A unittest blog entry', 
                u'markup': u'6', # Creole
                u'content': u'The unittest blog content',
                u'is_public': u'on', 
                u'new_tags': u'unittest blog tags',
                u'save': u'save',
            }
        )
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(
                "New blog entry created.",
                "New tags created:", "unittest", "blog", "tags",
                "blog - all entries","tag cloud", "syndication feeds",
            ),
            must_not_contain=("Traceback", "Error",),
        )
        
        # Get the blog entry detail page as a staff user
        response = self.client.get(self.detail_url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(
                "A unittest blog entry",
                "published by staff test user",
                "Leave a comment",
                "staff_test_user@example.org",
                "http://testserver",
            ),
            must_not_contain=("Traceback", "Error",),
        )
        
        # Leave a comment as a staff user
        response = self.client.post(
            self.detail_url,
            {
                u'person_name': u'the person name',
                u'email': u'email@address.tld',
                u'homepage': u'http://homepage.tld',
                u'content': u'the comment content.',
            }
        )
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(
                "Your comment saved.",
                "comments",
                "the person name", "the comment content.",
            ),
            must_not_contain=("Traceback", "Error",),
        )
        
        # TODO:
#        self.client.logout()
#        # Leave a comment as a anonymous user
#        response = self.client.post(
#            self.detail_url,
#            {
#                u'person_name': u'anonymous name',
#                u'email': u'email@address.tld',
#                u'homepage': u'http://homepage.tld',
#                u'content': u'the anonymous comment content.',
#            }
#        )
#        self.failUnlessEqual(response.status_code, 200)
#        self.assertResponse(
#            response,
#            must_contain=(
#                "Your comment saved.",
#                "comments",
#                "the person name", "the comment content.",
#            ),
#            must_not_contain=("Traceback", "Error",),
#        )
        


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
