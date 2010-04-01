#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - related test in pylucid/tests/test_i18n.py
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import Language


class LanguagePluginTest(basetest.BaseLanguageTestCase):
    """
    inherited from BaseUnittest:
        - initial data fixtures with default test users
        - self.login()
    
    inherited from BaseLanguageTest:
        - self.default_language - system default Language model instance (default: en instance)
        - self.default_language - alternative language code than system default (default: 'de')
        - self.other_language - alternative Language mode instance (default: de instance)
        - assertContentLanguage() - Check if response is in right language
    """
    def test_language_switch(self):
        """
        request root page without any HTTP_ACCEPT_LANGUAGE
        the default language should be returned
        """
        # first request must return default language
        response = self.client.get("/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertContentLanguage(response, self.default_language)

        # Switch language must rediret to new url with new language code
        response = self.client.get("/?language=" + self.other_lang_code)
        self.assertRedirect(response, url="http://testserver/de/", status_code=302)

        # After language switch, we must get the switched language
        response = self.client.get("/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertContentLanguage(response, self.other_language)

    def test_not_existing(self):
        """
        request a not existing language
        Note: "not-exist" is a valid language, see: django_tools.validators.validate_language_code
        """
        response = self.client.get("/?language=not-exist") # lang code is valid
        self.failUnlessEqual(response.status_code, 200)
        self.assertContentLanguage(response, self.default_language)

        # No debug info should be present
        self.assertResponse(response,
            must_not_contain=("Traceback", "Wrong lang code")
        )

    def test_wrong_format(self):
        """
        request a not existing language
        """
        response = self.client.get("/?language=wrong format!") # lang code is not valid
        self.failUnlessEqual(response.status_code, 200)
        self.assertContentLanguage(response, self.default_language)

        # No debug info should be present
        self.assertResponse(response,
            must_not_contain=("Traceback", "Wrong language code", "Enter a valid language code")
        )


#__test__ = {"doctest": """
#Another way to test that 1 + 1 is equal to 2.
#
#>>> 1 + 1 == 2
#True
#"""}

if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=1)
