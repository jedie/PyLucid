#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test for the page admin Plugin.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2008-02-29 12:09:14 +0100 (Fr, 29 Feb 2008) $
    $Rev: 1454 $
    $Author: JensDiemer $

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import tests
from tests.utils.BrowserDebug import debug_response

from django.conf import settings

from PyLucid.models import Page

# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True


MINIMAL_POST = {
    "save": "save", # The save button values
    "content": "Test content.",
    "name": "Test page name",
    "parent": "0", # Root
    "markup": 1,

}
COMPLETE_POST = MINIMAL_POST
COMPLETE_POST.update({
    "edit_comment": "The comment",
    "title": "The longer page title",
    "keywords": "Some test keywords",
    "description": "A test description.",
})



class TestBase(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    def setUp(self):
        # Check that required middlewares are on.
        # Otherwise every unitest will fail ;)
        middlewares = (
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        )
        self.check_middlewares(middlewares)

        self.base_url = "/%s/1" % settings.COMMAND_URL_PREFIX
        self.method_url = self.base_url + "/page_admin/%s/"
        self.edit_url = self.method_url % "edit_page"

    #__________________________________________________________________________
    # Special asserts

    def assertEditSuccessful(self, response, post_data):
        """
        A page was edited.
        -Check if the response confirmed a successful edit page action.
        -Compare the data in the database.
        """
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(
                "Old page data archived.",
                "Page data updated."
            ),
            must_not_contain=("This field is required.","Form error!")
        )

        # Compare the post_data with the page data stored in the database
        page = Page.objects.get(name = post_data["name"])
        for field in page._meta.fields:
            field_name = field.column.replace('_id','')
            if not field_name in post_data:
                continue

            page_data = getattr(page, field_name)
            if field_name == "parent":
                if page_data == None:
                    page_data = "0"

            #print "check:", field_name
            self.assertEqual(page_data, post_data[field_name])



class TestAnonymous(TestBase):
    """
    Tests without login
    """
    def test_permission1(self):
        """
        Try some edit_page methods, without login.
        Must be updated manually, if the plugin config changed.
        """
        method_names = (
            "edit_page", "new_page", "delete_page", "select_edit_page",
            "delete_pages", "sequencing"
        )
        self.assertAccessDenied(self.base_url, "page_admin", method_names)

class TestNormalUser(TestBase):
    """
    Tests as a normal user.
    """
    def setUp(self):
        super(TestNormalUser, self).setUp()
        self.login("normal")

    def test_get_form(self):
        """
        Get a the edit page form
        """
        response = self.client.get(self.edit_url)
        #debug_response(response)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("Edit the CMS page","save","preview"),
            must_not_contain=("Traceback",)
        )

    def test_edit(self):
        """
        Send a save post action, without fields.
        """
        response = self.client.post(self.edit_url, {"save":"save"})
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(
                "This field is required.",
                "Edit the CMS page","save","preview"
            ),
            must_not_contain=("Traceback",)
        )

    def test_edit1(self):
        """
        Send a save post action, with minimalistic field data.
        """
        response = self.client.post(
            self.edit_url, MINIMAL_POST
        )
        self.assertEditSuccessful(response, MINIMAL_POST)

    def test_edit1(self):
        """
        Send a save post action, with minimalistic field data.
        """
        response = self.client.post(
            self.edit_url, MINIMAL_POST
        )
        self.assertEditSuccessful(response, MINIMAL_POST)


    def test_edit1(self):
        """
        Send a save post action, with minimalistic field data.
        """
        response = self.client.post(
            self.edit_url, COMPLETE_POST
        )
        self.assertEditSuccessful(response, COMPLETE_POST)


#        debug_response(response)
#        self.failUnlessEqual(response.status_code, 200)
#        self.assertResponse(
#            response,
#            must_contain=(
#                "Old page data archived.",
#                "Page data updated."
#            ),
#            must_not_contain=("This field is required.","Form error!")
#        )



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])