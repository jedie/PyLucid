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

from PyLucid.models import Page, Plugin

ONE_BROWSER_TRACEBACK = True

# Run test with:
PAGE_ID = 1


BLOG_POST_DATA1 = {
    u'headline': u'A unittest blog entry', 
    u'markup': u'6', # Creole
    u'content': u'The unittest blog content',
    u'is_public': u'on', 
    u'new_tags': u'unittest blog tags',
}


class TestPluginBlog(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []
   
    def __init__(self, *args, **kwargs):
        super(TestPluginBlog, self).__init__(*args, **kwargs)

        from PyLucid.plugins_internal.blog import blog_cfg
        self.blog_cfg = blog_cfg
        
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
        
    def test_blog_entry_preview(self):
        """
        Test the markup preview
        """
        self.login("staff")
        
        post_data = {
            u'headline': u'preview test', 
            u'markup': u'6', # Creole
            u'content': u'[[url|title]]\n*list1\n*list2',
            u'preview': u'preview'
        }
        
        # Create a new blog entry
        response = self.client.post(self.add_entry_url, post_data)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(
                '<p><a href="url">title</a></p>',
                "<li>list1</li>", "<li>list2</li>",
                "preview",
                "Create a new blog entry",
                "save", "preview", "abort",
            ),
            must_not_contain=("Traceback", "Error",),
        )
        
    def _create_new_blog_entry(self):
        """
        Create a blog entry.
        """
        self.login("staff")
        
        post_data = BLOG_POST_DATA1.copy()
        post_data.update({u'save': u'save'})
        
        # Create a new blog entry
        response = self.client.post(self.add_entry_url, post_data)
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
        
    def test_create_new_blog_entry(self):
        """
        as staff user:
        1. create a new blog entry
        2. Leave a comment 
        """
        self._create_new_blog_entry()
        
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
        
    def test_anonymous_comment(self):
        """
        Try to leave a comment as a anonymous user
        """
        self._create_new_blog_entry()
        self.client.logout()
        
        commend_data = {
            u'person_name': u'anonymous name',
            u'email': u'email@address.tld',
            u'homepage': u'http://homepage.tld',
            u'content': u'the anonymous comment content.',
        }
        
        def test(check_referer, referer, must_contain):
            """
            1. setup check_refere mode in the blog preferences
            2. sent the post data
            3. check the response
            """
            Plugin.objects.set_preferences(
                plugin_name="blog",
                key = 'check_referer',
                value = check_referer,
                user=None, id=None
            )
            
            response = self.client.post(
                self.detail_url,
                commend_data,
                HTTP_REFERER=referer,
            )
            self.failUnlessEqual(response.status_code, 200)
            self.assertResponse(
                response,
                must_contain=must_contain,
                must_not_contain=("Traceback", "Error",),
            )
                
        # Test with wrong http refere and "moderate" mode
        test(
            check_referer=self.blog_cfg.MODERATED,
            referer = "wrong",
            must_contain=(
                "Your comment must wait for authorization.",
                "Your comment saved.",
                "comments", "there exist no comment",
            )
        )
        
        # Test with wrong http refere and "spam reject" mode
        test(
            check_referer=self.blog_cfg.REJECT_SPAM,
            referer = "wrong",
            must_contain=(
                "Sorry, your comment identify as spam.",
                "comments", "there exist no comment",
            )
        )
        
        # Test with the right referer
        test(
            check_referer=self.blog_cfg.MODERATED,
            referer = "http://testserver/_command/1/blog/detail/1/",
            must_contain=(                
                "Your comment saved.",
                "comments",
                "anonymous name", "the anonymous comment content.",
            )
        )
        
        


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
