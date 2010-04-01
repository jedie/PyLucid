#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" lexicon entry in english and german
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageContent

from lexicon.models import LexiconEntry


SUMMARY_URL = "/%s/lexicon/"
ENTRY_URL = "/%s/lexicon/detail/PyLucid%%20CMS/"


class LexiconPluginTestCase(basetest.BaseLanguageTestCase):
    """
    inherited from BaseUnittest:
        - initial data fixtures with default test users
        - self.login()
    
    inherited from BaseLanguageTest:
        - self.default_language - system default Language model instance (default: en instance)
        - self.other_lang_code - alternative language code than system default (default: 'de')
        - self.other_language - alternative Language mode instance (default: de instance)
        - assertContentLanguage() - Check if response is in right language
    """
    SUMMARY_MUST_CONTAIN_EN = (
        '<a href="/en/lexicon/detail/PyLucid%20CMS/">PyLucid CMS</a>',
        '<dd>PyLucid is the CMS thats built this page.</dd>',
    )
    SUMMARY_MUST_CONTAIN_DE = (
        '<a href="/de/lexicon/detail/PyLucid%20CMS/">PyLucid CMS</a>',
        '<dd>PyLucid ist ein flexibles, Open Source Webseiten Content Management System.</dd>',
    )
    ENTRY_MUST_CONTAIN_EN = (
        '<a href="/en/lexicon/detail/PyLucid CMS/" title="PyLucid CMS', # breadcrumbs
        '<dd>PyLucid CMS</dd>',
        '<dt>Short definition:</dt>',
        '<p>This pages are created by PyLucid ;)</p>',
        '<legend>Leave a comment</legend>', # comments
    )
    ENTRY_MUST_CONTAIN_DE = (
        '<a href="/de/lexicon/detail/PyLucid CMS/" title="PyLucid CMS', # breadcrumbs
        '<dd>PyLucid CMS</dd>',
        '<dt>Kurzdefinition:</dt>',
        '<p>Diese Seiten werden mit PyLucid CMS generiert ;)</p>',
        '<legend>Leave a comment</legend>', # comments
    )
    ENTRY_MUST_CONTAIN_ES = (
        '<a href="/es/lexicon/detail/Spanish/" title="Spanish: Spanish is a language ;)"', # breadcrumbs
        '<dd>Spanish</dd>',
        '<dt>contenido:</dt>',
        '<p>Spanish or Castilian (español or castellano) is a Romance language...</p>',
        'Comentario', # comments
    )

    def assertLexiconPage(self, response, must_contain):
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response, must_contain=must_contain,
            must_not_contain=("Traceback",)
        )

    def assertSummaryEN(self, response):
        self.assertLexiconPage(response, must_contain=self.SUMMARY_MUST_CONTAIN_EN)

    def assertSummaryDE(self, response):
        self.assertLexiconPage(response, must_contain=self.SUMMARY_MUST_CONTAIN_DE)

    def assertEntryEN(self, response):
        self.assertLexiconPage(response, must_contain=self.ENTRY_MUST_CONTAIN_EN)

    def assertEntryDE(self, response):
        self.assertLexiconPage(response, must_contain=self.ENTRY_MUST_CONTAIN_DE)

    def assertEntryES(self, response):
        self.assertLexiconPage(response, must_contain=self.ENTRY_MUST_CONTAIN_ES)


class LexiconPluginTest1(LexiconPluginTestCase):
    """
    Tests with existing lexicon entries
    """
    def test_summary_en(self):
        response = self.client.get(
            SUMMARY_URL % self.default_language.code,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertSummaryEN(response)
        self.assertContentLanguage(response, self.default_language)

    def test_summary_de(self):
        response = self.client.get(
            SUMMARY_URL % self.other_language.code,
            HTTP_ACCEPT_LANGUAGE=self.other_language.code,
        )
        self.assertSummaryDE(response)
        self.assertContentLanguage(response, self.other_language)

    def test_lexicon_entry_en(self):
        response = self.client.get(
            ENTRY_URL % self.default_language.code,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertEntryEN(response)
        self.assertContentLanguage(response, self.default_language)

    def test_lexicon_entry_de(self):
        response = self.client.get(
            ENTRY_URL % self.other_language.code,
            HTTP_ACCEPT_LANGUAGE=self.other_language.code,
        )
        self.assertEntryDE(response)
        self.assertContentLanguage(response, self.other_language)

    def test_switch_url_language(self):
        """
        Request german language entry, but english ist current language
        -> redirect to english url
        """
        response = self.client.get(
            ENTRY_URL % self.other_language.code,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertRedirect(
            response, url="http://testserver" + ENTRY_URL % self.default_language.code, status_code=302
        )


class LexiconPluginTest2(LexiconPluginTestCase, basetest.BaseMoreLanguagesTestCase):
    """
    Tests with some new lexicon entries
        
    inherited from BaseMoreLanguagesTestCase:
        - created languages: "es", "es-ar", "pt", "hr"
        - self.languages - A dict with language code as keys and language instance as values   
    """
    def _pre_setup(self, *args, **kwargs):
        """ create some blog articles """
        super(LexiconPluginTest2, self)._pre_setup(*args, **kwargs)

        defaults = {
            "markup": PageContent.MARKUP_CREOLE,
            "is_public": True,
        }

        self.entry_es = self.easy_create(LexiconEntry, defaults,
            term="Spanish",
            language=self.languages["es"],
            tags="shared, Spain, other",
            short_definition="Spanish is a language ;)",
            content="Spanish or Castilian (español or castellano) is a Romance language...",
        )

    def test_es_entry(self):
        response = self.client.get("/es/lexicon/detail/Spanish/", HTTP_ACCEPT_LANGUAGE="es")
        self.assertEntryES(response)

    def test_es_redirect(self):
        """
        the activated language is German, but we want a Spain lexicon entry -> Redirect to it 
        """
        response = self.client.get(
            "/es/lexicon/detail/Spanish/",
            HTTP_ACCEPT_LANGUAGE="not-exist;q=0.9,de;q=0.8,pt-br;q=0.7,es;q=0.5"
        )
        self.assertRedirect(
            response, url="http://testserver/es/lexicon/detail/Spanish/", status_code=302
        )


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
#    management.call_command('test', "pylucid_plugins.lexicon.tests.LexiconPluginTest", verbosity=0)
    management.call_command('test', __file__, verbosity=1)
