#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test for the page admin Plugin.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import tests
from tests.utils.BrowserDebug import debug_response

from django.conf import settings

from PyLucid.models import Page, PageArchiv
from PyLucid.db.page_archiv import get_archivelist, get_last_archived_page

# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True


PAGE_ID = 1

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
PREVIEW_POST = MINIMAL_POST.copy()
del(PREVIEW_POST["save"])
PREVIEW_POST["preview"] = "preview"


OLD_PAGE_DATA = {
    "name": "old page",
    "title": "This is the old page",
    "content": "This is a old page content!",
    "keywords": "Some old test keywords",
    "description": "A old test description.",
}

ESC_TEST_CONTENT = (
    '{% if 1 %}\n'
    '{{ "xxx"|upper }}\n'
    '-\n'
    '{{ 123456789|filesizeformat }}\n'
    '{% endif %}'
)
ESC_TEST_VALUE = (
    'XXX\n'
    '-\n'
    '117.7 MB'
)
ESC_TEST_ESCAPED = (
    '&#x7B;% if 1 %&#x7D;\n'
    '&#x7B;&#x7B; "xxx"|upper &#x7D;&#x7D;\n'
    '-\n'
    '&#x7B;&#x7B; 123456789|filesizeformat &#x7D;&#x7D;\n'
    '&#x7B;% endif %&#x7D;'
)
ESC_TEST_ERROR = "{% a error ! %}"



class TestBase(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    def setUp(self):
        settings.DEBUG=False

        self.base_url = "/%s/%s" % (settings.COMMAND_URL_PREFIX, PAGE_ID)
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

    def test_minimal_edit(self):
        """
        Send a save post action, with minimalistic field data.
        """
        response = self.client.post(
            self.edit_url, MINIMAL_POST
        )
        self.assertEditSuccessful(response, MINIMAL_POST)


    def test_complete_edit(self):
        """
        Send a save post action, with minimalistic field data.
        """
        response = self.client.post(
            self.edit_url, COMPLETE_POST
        )
        self.assertEditSuccessful(response, COMPLETE_POST)

    def test_page_archiv(self):
        """
        Test the page archiv.

        The page admin plugin archives a page, after it was edited.
        We examine here archives data in a loop:
        1. set the current page with initial values
        2. edit the current page with self.test_complete_edit()
        3. check the archive:
           3.1. check the number of archive entries
           3.2. check the data of the last entry
        """
        def setup_old_page(edit_no):
            """
            set init data on the current page
            """
            old_page = Page.objects.get(id = PAGE_ID)
            for key, value in OLD_PAGE_DATA.iteritems():
                setattr(old_page, key, "%s - %s" % (value, edit_no))
            old_page.save()

        def assert_page_archiv(edit_no):
            """
            Check the archive
            """
            # Get the edit page object
            original_page = Page.objects.get(id = PAGE_ID)

            # check the number of archive entries
            assert len(get_archivelist(original_page)) == edit_no

            # check the data of the last entry
            archive = get_last_archived_page(original_page)
            for key, value in OLD_PAGE_DATA.iteritems():
                old_value = getattr(archive, key)
                #print key, old_value
                self.assertEqual(old_value, "%s - %s" % (value, edit_no))


        for edit_no in xrange(1,10):
            #print ">>> edit_no:", edit_no

            # Set init values
            setup_old_page(edit_no)

            # Edit the current page with COMPLETE_POST:
            self.test_complete_edit()

            # Check the page archiv
            assert_page_archiv(edit_no)

    def test_escaping_on(self):
        """
        Test the django tag escaping in preview (escaping on)

        It's not so easy to test, if the escaping works. Because there always a
        escaped version of the content in the editor textarea ;)
        So we used some django filter.

        If escaping not on, we shouldn't see the the end result ESC_TEST_VALUE.
        """
        post_data = PREVIEW_POST.copy()
        post_data["preview_escape"] = "on"
        post_data["content"] = ESC_TEST_CONTENT

        response = self.client.post(self.edit_url, post_data)
        #debug_response(response)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("preview", ESC_TEST_ESCAPED),
            must_not_contain=(ESC_TEST_VALUE,)
        )

    def test_escaping_off1(self):
        """
        Test the django tag escaping in preview (escaping off)

        The django template engine should create ESC_TEST_VALUE
        """
        post_data = PREVIEW_POST.copy()
        #post_data["preview_escape"] = "" # Off
        post_data["content"] = ESC_TEST_CONTENT

        response = self.client.post(self.edit_url, post_data)
        #debug_response(response)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("preview", ESC_TEST_VALUE,),
        )

    def test_escaping_off2(self):
        """
        Test without escaping and a invalide django template construct.
        """
        post_data = PREVIEW_POST.copy()
        post_data["content"] = ESC_TEST_ERROR

        response = self.client.post(self.edit_url, post_data)
        #debug_response(response)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(
                "edit_page Error", "TemplateSyntaxError", "Invalid block tag"
            ),
        )





if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
