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

if __name__ == "__main__":
    # run unittest directly
    import os
#    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"
    os.environ["DJANGO_SETTINGS_MODULE"] = "pylucid_project.pylucid_plugins.auth.test_settings"
    virtualenv_file = "../../../../../../PyLucid_env/bin/activate_this.py"
    execfile(virtualenv_file, dict(__file__=virtualenv_file))

from django.test import TestCase

#class AuthTest(TestCase):
#    fixtures = ['pylucid.json']
#
#    def test_basic_addition(self):
#        """
#        Tests that 1 + 1 always equals 2.
#        """
#        self.failUnlessEqual(1 + 1, 2)
#
#__test__ = {"doctest": """
#Another way to test that 1 + 1 is equal to 2.
#
#>>> 1 + 1 == 2
#False
#"""}


from django.test.client import Client
from django_tools.unittest_utils import unittest_base, BrowserDebug

from pylucid_project.tests.test_tools import basetest


LOGIN_URL = "?auth=login"


class LoginTest(basetest.BaseUnittest):
    fixtures = ['pylucid.json']

    def setUp(self):
        self.client = Client() # start a new session

    def test_login_link(self):
        """ Simple check if login link exist. """
        response = self.client.get("/admin/", HTTP_ACCEPT_LANGUAGE="en")
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

#    def test_login_get_form(self):
#        """ Simple check if login link exist. """
#        response = self.client.get(LOGIN_URL)
#        self.assertResponse(response,
#            must_contain=(
#                '<title>1-rootpage title', # PageContent
#                # Form stuff:
#                "JS-SHA-LogIn", "username", "sha_login", "next_url"
#            ),
#            must_not_contain=(
#                "Traceback", 'Permission denied'
#                '1-rootpage content', # PageContent
#            ),
#        )
#
#    def test_login_ajax_form(self):
#        """ Check if we get the login form via AJAX """
#        response = self.client.get(LOGIN_URL, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
#        self.failUnlessEqual(response.status_code, 200)
#        self.assertResponse(response,
#            must_contain=(
#                # Form stuff:
#                "JS-SHA-LogIn", "username", "sha_login", "next_url"
#            ),
#            must_not_contain=(
#                '<title>1-rootpage title', "<body", "<head>", # <- not a complete page
#                "Traceback", 'Permission denied'
#                '1-rootpage content', # PageContent
#            ),
#        )



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=1)
