#!/usr/bin/env python
# coding: utf-8

"""
    i18n unittests
    ~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - related test in pylucid_plugins/language/tests.py
    
    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
from django.utils.log import getLogger
import logging

if __name__ == "__main__":
    # Run all unittest directly

    tests = __file__
#    tests = "pylucid.tests.test_i18n.TestI18n.test_other_language_in_url"

    from pylucid_project.tests import run_test_directly
    run_test_directly(tests,
        verbosity=2,
#        failfast=True,
        failfast=False,
    )
    sys.exit()

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.cache import cache

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import Language


class TestI18nWithCache(basetest.BaseLanguageTestCase):
    def test_other_language_in_url(self):
        """
        Request a English page as a German user.
        """
        #self.enable_i18n_debug()

        cache.clear()
        response = self.client.get("/en/welcome/", HTTP_ACCEPT_LANGUAGE="de-de,de;q=0.8,en-us;q=0.5,en;q=0.3")
        self.assertRedirect(response, url="http://testserver/de/welcome/", status_code=301)


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
    def setUp(self):
        cache.clear()

    def test_no_accept_language(self):
        """
        request root page without any HTTP_ACCEPT_LANGUAGE
        the default language should be returned
        """
        response = self.client.get("/")
        self.assertRedirect(response, url="http://testserver/en/welcome/", status_code=302)

        response = self.client.get("/en/welcome/")
        self.assertStatusCode(response, 200)
        self.assertContentLanguage(response, self.default_language)

    def test_accept_language_de(self):
        """
        we must get german.
        """
        accept_languages = "de-de,de;q=0.8,en-us;q=0.5,en;q=0.3"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_languages)
        self.assertRedirect(response, url="http://testserver/de/welcome/", status_code=302)

        response = self.client.get("/de/welcome/", HTTP_ACCEPT_LANGUAGE=accept_languages)
        self.assertStatusCode(response, 200)
        self.assertContentLanguage(response, self.other_language)

    def test_fallback_language(self):
        """ the first part of a language code must be used as a fallback """
        accept_languages = "de-AT;q=0.9,de-de;q=0.8,en-us;q=0.5"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_languages)
        self.assertRedirect(response, url="http://testserver/de/welcome/", status_code=302)

    def test_no_lang_code(self):
        """
        test pylucid.views.resolve_url: url without a language code, should redirect to full url
        """
        response = self.client.get("/example-pages/markups/", HTTP_ACCEPT_LANGUAGE="de-de,de;q=0.8,en-us;q=0.5,en;q=0.3")
        self.assertRedirect(response, url="http://testserver/de/example-pages/markups/", status_code=302)

    def test_page_without_lang(self):
        """
        test pylucid.views.page_without_lang: url without a language code, should redirect to full url
        """
        response = self.client.get("/welcome/", HTTP_ACCEPT_LANGUAGE="de-de,de;q=0.8,en-us;q=0.5,en;q=0.3")
        self.assertRedirect(response, url="http://testserver/de/welcome/", status_code=302)

    def test_not_existing_language(self):
        """
        test pylucid.views.page_without_lang: url without a language code, should redirect to full url
        """
        response = self.client.get("/hr/", HTTP_ACCEPT_LANGUAGE="en-us;q=0.5,en;q=0.3")
        self.assertRedirect(response, url="http://testserver/en/", status_code=301)

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

        response = self.client.get("/de/welcome/", HTTP_ACCEPT_LANGUAGE=lang_code)
        self.assertRedirect(response, url="http://testserver/en/welcome/", status_code=301)

    def test_no_language_on_site(self):
        """
        replace the site on all languages, with a not existing one.
        So we must fallback to the default language. 
        """
        test_site = Site(domain="not_exist.tld")
        test_site.save()

        # replace sites on all languages
        for language in Language.objects.all():
#            print language, language.sites.all()
            language.sites.clear()
            language.sites.add(test_site)
#            print language, language.sites.all()

        response = self.client.get("/")
        self.assertRedirect(response, url="http://testserver/en/welcome/", status_code=302)

        response = self.client.get("/en/welcome/")
        self.assertResponse(response,
            must_contain=("<body", 'Welcome to your PyLucid CMS =;-)'),
            must_not_contain=("Traceback",)
        )


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
    def setUp(self):
        cache.clear()

    def assertItsCroatian_with_en(self, response):
        """
        Croatian doesn't exist. But it's a supported language.
            - The ContentPage is in EN
            - gettext translations works and used croatian.
        """
        self.assertStatusCode(response, 200)
        self.assertContentLanguage(response, self.default_language)
        self.assertResponse(response,
            must_contain=(
                '<html lang="en">',
                '<h2 id="page_title">Welcome to your PyLucid CMS =;-)</h2>',
                '''<strong title="Current used language is 'Croatian'.">Croatian</strong>''',
                '>Prijavi se<', # 'Login in' translated in croatian 
            ),
            must_not_contain=("Traceback",)
        )

    def assertItsCroatian_with_de(self, response):
        """
        Croatian doesn't exist. But it's a supported language.
            - The ContentPage is in DE
            - gettext translations works and used croatian.
        """
        self.assertStatusCode(response, 200)
        self.assertContentLanguage(response, self.other_language)
        self.assertResponse(response,
            must_contain=(
                '<html lang="de">',
                '<h2 id="page_title">Willkommen auf deiner PyLucid CMS Seite =;-)</h2>',
                '''<strong title="Current used language is 'Croatian'.">Croatian</strong>''',
                '>Prijavi se<', # 'Login in' translated in croatian 
            ),
            must_not_contain=("Traceback",)
        )

    def assertItsNotCroation_its_de(self, response):
        self.assertContentLanguage(response, self.other_language)
        self.assertResponse(response,
            must_contain=(
                '<html lang="de">',
                '<h2 id="page_title">Willkommen auf deiner PyLucid CMS Seite =;-)</h2>',
                '''<strong title="Current used language is 'Deutsch'.">Deutsch</strong>''',

            ),
            must_not_contain=("Traceback",
                '''<strong title="Current used language is 'Croatian'.">Croatian</strong>''',
                'Prijavi se', # 'Login in' translated in croatian
            )
        )

    def test_language_exists(self):
        """ test if we really have more languages ;) """
        self.failUnless(Language.objects.count() >= 6)

    def test_cache_language_collision(self):
#        self.enable_i18n_debug()

#        logger = getLogger("PyLucidCacheMiddleware")
#        logger.setLevel(logging.DEBUG)
#        logger.addHandler(logging.StreamHandler())

        accept_language = "hr;q=0.8,en;q=0.3"

        response = self.client.get("/de/welcome/", HTTP_ACCEPT_LANGUAGE=accept_language)
        redirected_url = "http://testserver/en/welcome/"
        self.assertRedirect(response, url=redirected_url, status_code=301)
        self.assertFalse(response._from_cache)

        # add hr to cache
        response = self.client.get(redirected_url, HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertItsCroatian_with_en(response)
        self.assertFalse(response._from_cache)

        # add de to cache
        response = self.client.get("/de/welcome/", HTTP_ACCEPT_LANGUAGE="de")
        self.assertItsNotCroation_its_de(response)
        self.assertFalse(response._from_cache)

        # check hr cached version:
        response = self.client.get(redirected_url, HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertItsCroatian_with_en(response)
        self.assertTrue(response._from_cache)

        # check de cached version:        
        response = self.client.get("/de/welcome/", HTTP_ACCEPT_LANGUAGE="de")
        self.assertItsNotCroation_its_de(response)
        self.assertTrue(response._from_cache)

    def test_accept_language_hr_fallback_to_en(self):
        accept_language = "hr;q=0.8,en;q=0.3"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_language)
        redirected_url = "http://testserver/en/welcome/"
        self.assertRedirect(response, url=redirected_url, status_code=302)
        response = self.client.get(redirected_url, HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertItsCroatian_with_en(response)

    def test_accept_language_hr_fallback_to_de(self):
        accept_language = "hr;q=0.8,de;q=0.3"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_language)
        redirected_url = "http://testserver/de/welcome/"
        self.assertRedirect(response, url=redirected_url, status_code=302)
        response = self.client.get(redirected_url, HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertItsCroatian_with_de(response)

    def test_accept_language_hr_fallback_to_default(self):
        accept_language = "hr;q=0.8,xx;q=0.3"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_language)
        redirected_url = "http://testserver/en/welcome/"
        self.assertRedirect(response, url=redirected_url, status_code=302)
        response = self.client.get(redirected_url, HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertItsCroatian_with_en(response)

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
        redirected_url = "http://testserver/en/welcome/"
        self.assertRedirect(response, url=redirected_url, status_code=302)
        response = self.client.get(redirected_url, HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertItsCroatian_with_en(response)

    def test_not_exist_language(self):
        accept_language = "not-exist;q=0.9,ja;q=0.8"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_language)
        redirected_url = "http://testserver/en/welcome/"
        self.assertRedirect(response, url=redirected_url, status_code=302)
        response = self.client.get(redirected_url, HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertContentLanguage(response, self.default_language)

    def test_fallback_language_anonymous(self):
        """
        "pt-br"  (Brazilian Portuguese) is not installed, but "pt" (Portuguese) exist.
        PyLucid must fallback to pt, even if it's not in accept language
        
        Anonymous users didn't get a information message, cause of not cacheable if messages exist
        """
        accept_language = "not-exist;q=0.9,pt-br;q=0.8"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_language)
        redirected_url = "http://testserver/en/welcome/"
        self.assertRedirect(response, url=redirected_url, status_code=302)
        response = self.client.get(redirected_url, HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertContentLanguage(response, self.default_language)
        self.assertResponse(response,
            must_contain=(
                '''<strong title="Current used language is 'Portuguese'.">Portuguese</strong>''',
                '>Entrar<', # 'Login in' translated in Portuguese 
            ),
            must_not_contain=("Traceback",)
        )

    def test_fallback_language_user_information(self):
        """
        "pt-br"  (Brazilian Portuguese) is not installed, but "pt" (Portuguese) exist.
        PyLucid must fallback to pt, even if it's not in accept language
        """
        self.login("normal") # users get a messages

        accept_language = "not-exist;q=0.9,pt-br;q=0.8"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_language)
        redirected_url = "http://testserver/en/welcome/"
        self.assertRedirect(response, url=redirected_url, status_code=302)
        response = self.client.get(redirected_url, HTTP_ACCEPT_LANGUAGE=accept_language)
        self.assertContentLanguage(response, self.default_language)
        self.assertResponse(response,
            must_contain=(
                '<a href="?auth=logout">Sair [normal test user]</a>', # logout in Portuguese
                '''<strong title="Current used language is 'Portuguese'.">Portuguese</strong>''',
                'PageMeta welcome doesn&#39;t exist in client favored language Portuguese, use English entry.',
            ),
            must_not_contain=("Traceback",)
        )


