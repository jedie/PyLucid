# coding:utf-8

import test_tools # before django imports!

#from django_tools.utils import info_print; info_print.redirect_stdout()

from django_tools.unittest import unittest_base, BrowserDebug

from pylucid_project.tests.test_tools import basetest


LOGIN_URL = "?auth=login"


class LoginTest(basetest.BaseUnittest):
    def test_login_link(self):
        """ Simple check if login link exist. """
        response = self.client.get("/")
        self.assertResponse(response,
            must_contain=(
                # PageContent:
                '1-rootpage content',
                '<title>1-rootpage title',
                # Login in link:
                '<span class="PyLucidPlugins auth" id="auth_lucidTag">',
                '<a href="?auth=login"',
                'id="login_link',
            ),
            must_not_contain=('Error', "traceback", 'Permission denied'),
        )

    def test_login_get_form(self):
        """ Simple check if login link exist. """
        response = self.client.get(LOGIN_URL)
        self.assertResponse(response,
            must_contain=(
                '<title>1-rootpage title', # PageContent
                # Form stuff:
                "JS-SHA-LogIn", "username", "sha_login", "next_url"
            ),
            must_not_contain=(
                "Traceback", 'Permission denied'
                '1-rootpage content', # PageContent
            ),
        )

    def test_login_ajax_form(self):
        """ Check if we get the login form via AJAX """
        response = self.client.get(LOGIN_URL, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                # Form stuff:
                "JS-SHA-LogIn", "username", "sha_login", "next_url"
            ),
            must_not_contain=(
                '<title>1-rootpage title', "<body", "<head>", # <- not a complete page
                "Traceback", 'Permission denied'
                '1-rootpage content', # PageContent
            ),
        )


if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__) # run all test from this file

#    from django.core import management
#    management.call_command('test', "test_PluginEditPage.CreateNewContentTest")
