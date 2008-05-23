#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the API to the internal page files.

    TODO:
        - Check .css and .js file, too.
        - Check all rellay used internal pages (Parse all plugins)

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""
import os

import tests
from tests.utils.FakeRequest import get_fake_context

from django.conf import settings

from PyLucid.system import internal_page
from PyLucid.models import Page

# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True

# A minimalistic template, how contains only needfull information
TEST_TEMPLATE = (
    "{% if messages %}"
    "{% for message in messages %}{{ message }}\n{% endfor %}"
    "{% endif %}"
    "\n"
    "{{ PAGE.content }}"
)

TEST_CONTENT = "This is a test content..."

class InternalPageTest(tests.TestCase):

    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    def setUp(self):
        self.fake_context = get_fake_context()
        Page.objects.all().delete() # Delete all existins pages

        self.template = tests.create_template(content = TEST_TEMPLATE)

        # Create the test pages defined in content_test_utils.py
        # assign the test template to all pages
        tests.create_pages(
            tests.TEST_PAGES,
            template=self.template,
        )

    #--------------------------------------------------------------------------

    def _get_filepath(self, internal_page_dir, plugin_name, internal_page_name,
                                                                         slug):
        return os.path.join(
            settings.MEDIA_ROOT,
            settings.PYLUCID_MEDIA_DIR,
            internal_page_dir,
            plugin_name,
            internal_page_name + "." + slug
        )

    def _get_file(self, internal_page_dir, plugin_name, internal_page_name,
                                                                         slug):

        file_path = self._get_filepath(
            internal_page_dir, plugin_name, internal_page_name, slug
        )
        content = file(file_path, "r").read()
        content = content.decode(settings.FILE_CHARSET)
        return content

    def _get_default_ipage(self, plugin_name, internal_page_name, slug):
        """
        returns the file content of a file in the default internal page dir
        """
        return self._get_file(
            settings.INTERNAL_PAGE_DIR,
            plugin_name, internal_page_name, slug
        )

    def _get_custom_ipage(self, plugin_name, internal_page_name, slug):
        """
        returns the file content of a file in the custom internal page dir
        """
        return self._get_file(
            settings.CUSTOM_INTERNAL_PAGE_DIR,
            plugin_name, internal_page_name, slug
        )

    #--------------------------------------------------------------------------

    def test_get_internal_page(self):
        """
        Test a existing internal page
        """
        plugin_name = "auth"
        internal_page_name = "input_username"

        is_content = internal_page.get_internal_page(
            self.fake_context, plugin_name, internal_page_name
        )
        must_content = self._get_default_ipage(
            plugin_name, internal_page_name, "html"
        )
        assert is_content == must_content

    def test_wrong_page_name(self):
        """
        Test a wrong internal page name
        """
        self.assertRaises(
            internal_page.InternalPageNotFound,
            internal_page.get_internal_page,
                context = self.fake_context,
                plugin_name = "auth",
                internal_page_name = "not existing"
        )

    def test_wrong_plugin_name(self):
        """
        Test a wrong plugin name
        """
        self.assertRaises(
            internal_page.InternalPageNotFound,
            internal_page.get_internal_page,
                context = self.fake_context,
                plugin_name = "not existing",
                internal_page_name = "not existing"
        )

    def test_custom_ipage(self):
        """
        Create a custom internal page file and check if this page would be used
        and not the default one.

        -create the custom path e.g.: ./media/PyLucid/custom/auth
        -create the internal path file e.g.: ...custom/auth/input_username.html
        -get the internal page and compare the content
        -delete the test internal page file
        -delete all created path parts
        """
        plugin_name = "auth"
        internal_page_name = "input_username"

        # For the test it may not exist an custom file, yet.
        self.assertRaises(
            IOError,
            self._get_custom_ipage,
                plugin_name, internal_page_name, "html"
        )

        # Check if the path e.g. ./media/PyLucid/custom/auth/ exists
        # create and delete it, if is not exists
        base_path = os.path.join(
            settings.MEDIA_ROOT,
            settings.PYLUCID_MEDIA_DIR,
            settings.CUSTOM_INTERNAL_PAGE_DIR,
        )
        custom_path = os.path.join(base_path, plugin_name)
        paths = [
            [base_path, False], [custom_path, False]
        ]
        # Create all path parts, which doesn't exists yet.
        # Remember the created directories for later remove.
        for path in paths:
            if os.path.isdir(path[0]):
                path[1] = True
            else:
                os.mkdir(path[0])

        filepath = self._get_filepath(
            settings.CUSTOM_INTERNAL_PAGE_DIR,
            plugin_name, internal_page_name, "html"
        )
        try:
            # Create the custom internal page
            f = file(filepath, "w")
            f.write(TEST_CONTENT)
            f.close()

            # Get the content via the productive used function
            is_content = internal_page.get_internal_page(
                self.fake_context, plugin_name, internal_page_name
            )
            # Check if the content is the test content and not the default
            # internal page content
            assert is_content == TEST_CONTENT
        finally:
            try:
                # remove the test file
                os.remove(filepath)
            finally:
                # Remove all dir parts, how doesn't exists before the test
                paths.reverse()
                for path, exists in paths:
                    if exists == False:
                        os.rmdir(path)

    #--------------------------------------------------------------------------

    def test_real_request(self):
        """
        Test a login request, who used a internal page.
        """
        response = self.client.get("/_command/1/auth/login/")
        content = response.content

        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                "PyLucidPlugins auth", "auth_login",
                "Username:", "sha_button", "plaintext_button"
            )
        )

    def test_not_existing(self):
        """
        Test a request to a _command url with a not existing internal page.

        -rename a internal page for the login (/auth/input_username.html)
        -request the login page
        -check the error messages in the response
        """
        plugin_name = "auth"
        internal_page_name = "input_username"

        filepath = self._get_filepath(
            settings.INTERNAL_PAGE_DIR, plugin_name, internal_page_name, "html"
        )
        assert os.path.isfile(filepath)
        try:
            # rename the orignal internal page file
            os.rename(filepath, filepath + "_unittest")
            assert not os.path.isfile(filepath)

            response = self.client.get("/_command/1/auth/login/")
            self.assertResponse(response,
                must_contain=(
                    "Internal page 'input_username' not found!",
                ),
                must_not_contain=("Run plugin auth.login Error",)
            )
        finally:
            # rename back
            os.rename(filepath + "_unittest", filepath)
            assert os.path.isfile(filepath)



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
