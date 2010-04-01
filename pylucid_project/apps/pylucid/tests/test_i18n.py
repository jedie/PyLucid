#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - related test in pylucid_plugins/language/tests.py
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.contrib.auth.models import Group

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import Language


class TestI18n(basetest.BaseLanguageTestCase):
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
    def test_no_accept_language(self):
        """
        request root page without any HTTP_ACCEPT_LANGUAGE
        the default language should be returned
        """
        response = self.client.get("/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertContentLanguage(response, self.default_language)

    def test_accept_language_de(self):
        """
        we must get german.
        """
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="de-de,de;q=0.8,en-us;q=0.5,en;q=0.3")
        self.failUnlessEqual(response.status_code, 200)
        german = Language.objects.get(code="de")
        self.assertContentLanguage(response, german)

    def test_fallback_language(self):
        """ the first part of a language code must be used as a fallback """
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="de-AT;q=0.9,de-de;q=0.8,en-us;q=0.5")
        self.failUnlessEqual(response.status_code, 200)
        german = Language.objects.get(code="de")
        self.assertContentLanguage(response, german)

    def test_language_redirect(self):
        """
        The url must be changed, if we get a german page with a english url.
        """
        response = self.client.get("/en/welcome/", HTTP_ACCEPT_LANGUAGE="de-de,de;q=0.8,en-us;q=0.5,en;q=0.3")
        self.assertRedirect(response, url="http://testserver/de/welcome/", status_code=301)

    def test_permit_group(self):
        """
        Test if language.permitViewGroup works.
        """
        lang_code = "de"
        self.failUnless(lang_code != self.default_language.code)

        test_group = Group(name="language test")
        test_group.save()
        lang = Language.objects.get(code=lang_code)
        lang.permitViewGroup = test_group
        lang.save()

        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=lang_code)
        self.failUnlessEqual(response.status_code, 200)
        self.assertContentLanguage(response, self.default_language)



class TestI18nMoreLanguages(basetest.BaseMoreLanguagesTestCase):
    """
    inherited from BaseUnittest:
        - initial data fixtures with default test users
        - self.login()
    
    inherited from BaseLanguageTest:
        - self.default_language - system default Language model instance (default: en instance)
        - self.default_language - alternative language code than system default (default: 'de')
        - self.other_language - alternative Language mode instance (default: de instance)
        - assertContentLanguage() - Check if response is in right language
        
    inherited from BaseMoreLanguagesTestCase:
        - created languages: "es", "es-ar", "pt", "hr"
        - self.languages - A dict with language code as keys and language instance as values
    """
    def test_language_exists(self):
        """ test if we really have more languages ;) """
        self.failUnless(Language.objects.count() >= 6)

    def assertItsCroatian(self, response):
        """
        Croatian doesn't exist. But it's a supported language.
            - The ContentPage is in system default language.
            - gexttext works in croatian
        """
        self.failUnlessEqual(response.status_code, 200)
        self.assertContentLanguage(response, self.default_language)
        self.assertResponse(response,
            must_contain=(
                '''<strong title="Current used language is 'Croatian'.">Croatian</strong>''',
                'PageMeta welcome doesn&#39;t exist in client favored language Croatian, use English entry.',
                '>Prijavi se<', # 'Login in' translated in croatian 
            ),
            must_not_contain=("Traceback",)
        )

    def test_accept_language_hr(self):
        """       
        But Croatian must be active.
        """
        accept_language = "hr;q=0.8,en;q=0.3"

        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertItsCroatian(response)

    def test_use_first_supported(self):
        """
        Croatian doesn't exist. But it's a supported language.
        We must get the ContentPage in system default language.
        But Croatian must be active.
        
        pt-br, Brazilian Portuguese is not installed
        the first useable language is Croatian.
        """
        accept_language = "not-exist;q=0.9,pt-br;q=0.8,hr;q=0.8,en;q=0.3"

        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertItsCroatian(response)

    def test_not_exist_language(self):
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="not-exist;q=0.9,ja;q=0.8")
        self.failUnlessEqual(response.status_code, 200)
        self.assertContentLanguage(response, self.default_language)

    def test_fallback_language(self):
        """
        "pt-br"  (Brazilian Portuguese) is not installed, but "pt" (Portuguese) exist.
        PyLucid must fallback to pt, even if it's not in accept language
        """
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="not-exist;q=0.9,pt-br;q=0.8")
        self.failUnlessEqual(response.status_code, 200)
        self.assertContentLanguage(response, self.default_language)
        self.assertResponse(response,
            must_contain=(
                '''<strong title="Current used language is 'Portuguese'.">Portuguese</strong>''',
                'PageMeta welcome doesn&#39;t exist in client favored language Portuguese, use English entry.',
                '>Entrar<', # 'Login in' translated in Portuguese 
            ),
            must_not_contain=("Traceback",)
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
#    management.call_command('test', "pylucid.tests.test_i18n.TestI18n.test_fallback_language", verbosity=0)
    management.call_command('test', __file__,
        verbosity=1
#        verbosity=0
    )
