#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - related test in pylucid/tests/test_i18n.py
    
    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


from pylucid_project.tests.test_tools import basetest


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
        response = self.client.get("/en/")
        self.assertContentLanguage(response, self.default_language)
        self.assertStatusCode(response, 200)

        # Switch language must rediret to new url with new language code
        response = self.client.get("/en/?language=" + self.other_lang_code)
        self.assertRedirect(response, url="http://testserver/de/", status_code=302)

        # After language switch, we must get the switched language
        response = self.client.get("http://testserver/de/")
        self.assertContentLanguage(response, self.other_language)
        self.assertStatusCode(response, 200)

    def test_not_existing(self):
        """
        request a not existing language
        Note: "not-exist" is a valid language, see: django_tools.validators.validate_language_code
        """
        response = self.client.get("/en/?language=not-exist") # lang code is valid
        self.assertStatusCode(response, 200)
        self.assertContentLanguage(response, self.default_language)

        # No debug info should be present
        self.assertResponse(response,
            must_not_contain=("Traceback", "Wrong lang code")
        )

    def test_wrong_format(self):
        """
        request a not existing language
        """
        response = self.client.get("/en/?language=wrong format!") # lang code is not valid
        self.assertStatusCode(response, 200)
        self.assertContentLanguage(response, self.default_language)

        # No debug info should be present
        self.assertResponse(response,
            must_not_contain=("Traceback", "Wrong language code", "Enter a valid language code")
        )


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    tests = __file__
#    tests = "pylucid_plugins.language.tests.LanguagePluginTest"
#    tests = "pylucid_plugins.language.tests.LanguagePluginTest.test_wrong_format"

    management.call_command('test', tests,
        verbosity=2,
        failfast=True
    )
