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

from django.conf import settings
from django.test.client import Client
from django_tools.unittest_utils import unittest_base, BrowserDebug

from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.tests.test_tools import basetest

from preference_forms import AuthPreferencesForm


LOGIN_URL = "?auth=login"


class LoginTest(basetest.BaseUnittest):
    def setUp(self):
        self.client = Client() # start a new session

    def test_login_link(self):
        """ Simple check if login link exist. """
        response = self.client.get("/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertAdminLoginPage(response)
        
    def test_login_redirect(self):
        """
        Check login redirect
        http://github.com/jedie/PyLucid/issues#issue/6
        """
        response = self.client.get("/pylucid_admin/menu/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertRedirect(response, "http://testserver/admin/?next=/pylucid_admin/menu/")

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

    def test_DOS_attack(self):
        settings.DEBUG = True
        
        client = self.client
        userdata = self._get_userdata("normal")
        username=userdata["username"]
#        self.login("normal")
#        client.logout()
        
        # Get the login form: The channenge value would be stored into settion
        self.test_login_get_form()
        self.failUnless("challenge" in client.session)
        
        pref_form = AuthPreferencesForm()
        preferences = pref_form.get_preferences()
        ban_limit = preferences["ban_limit"]
        
        # Hold if all events would been received.
        tested_first_login = False
        tested_under_limit = False
        tested_limit_reached = False
        tested_banned = False
        
        for no in xrange(1, ban_limit+3):          
            # get the salt
            response1 = client.post(
                "/?auth=get_salt", {"username": username}, HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            response2 = client.post(
                "/?auth=sha_auth",
                {
                    "username": username,
                    "sha_a2": "0123456789abcdef0123456789abcdef01234567",
                    "sha_b": "0123456789abcdef0123",
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            
            if no==1:
                # first request, normal failed 
                tested_first_login = True
                self.failUnless(len(response1.content) == 5) # the salt          
                self.assertResponse(response2,
                    must_contain=(
                        'auth.authenticate() failed.',
                        'must be a wrong password)',
                    ),
                    must_not_contain=(
                        "Traceback", "Form errors", "field is required",
                        "<!DOCTYPE", "<body", "</html>",
                    )
                )
            elif no==ban_limit+1:
                # The limit has been reached
                tested_banned = True
                self.assertResponse(response2, must_contain=('Add IP to ban list.',))
                self.assertStatusCode(response2, 404)
                self.failUnless(len(response1.content) == 5) # the salt
            elif no>ban_limit:
                # IP is on the ban list
                tested_limit_reached = True
                self.assertStatusCode(response2, 403) # get forbidden page
                self.assertStatusCode(response1, 403) # get forbidden page
            else:
                # under ban limit: comment was saved, page should be reloaded
                tested_under_limit = True
                self.failUnless(len(response1.content) == 5) # the salt
                self.assertResponse(response2,
                    must_contain=(
                        'Request too fast!',
                        'IP is blocked by',
                    ),
                    must_not_contain=(
                        "Traceback", "Form errors", "field is required",
                        "<!DOCTYPE", "<body", "</html>",
                    )
                )
            
        # Check if all events have been received.
        self.failUnless(tested_first_login == True)
        self.failUnless(tested_limit_reached == True)
        self.failUnless(tested_under_limit == True)
        self.failUnless(tested_banned == True)


if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', __file__,
#        verbosity=0,
        verbosity=1,
#        verbosity=2,
        failfast=True
    )
