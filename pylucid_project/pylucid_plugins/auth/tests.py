# coding: utf-8

"""
    PyLucid JS-SHA-Login tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    A secure JavaScript SHA-1 Login and a plaintext fallback login.
    
    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.test import TestCase
from django.test.client import Client
from django_tools.unittest_utils import unittest_base, BrowserDebug

from pylucid_project.tests.test_tools import basetest


LOGIN_URL = "?auth=login"


class LoginTest(basetest.BaseUnittest):
    def setUp(self):
        self.client = Client() # start a new session

    def test_login_link(self):
        """ Simple check if login link exist. """
        response = self.client.get("/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertAdminLoginPage(response)

    def test_login_get_form(self):
        """ Simple check if login link exist. """
        response = self.client.get(LOGIN_URL)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS',
                "JS-SHA-LogIn", "username", "var challenge=",
                '<input id="submit_button" type="submit" value="Log in" />',
            ),
            must_not_contain=(
                "Traceback", 'Permission denied'
            ),
        )

    def test_login_ajax_form(self):
        """ Check if we get the login form via AJAX """
        response = self.client.get(LOGIN_URL, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<div class="PyLucidPlugins auth" id="auth_http_get_view">',
                "JS-SHA-LogIn", "username", "var challenge=",
                '<input id="submit_button" type="submit" value="Log in" />',
            ),
            must_not_contain=(
                '<title>PyLucid CMS', "<body", "<head>", # <- not a complete page
                "Traceback", 'Permission denied'
            ),
        )



if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=1)
