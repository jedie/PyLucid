#!/usr/bin/env python
# coding: utf-8


"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" lexicon entry in english and german
    
    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import sys


if __name__ == "__main__":
    # Run all unittest directly

    tests = __file__
#    tests = "pylucid_plugins.lexicon.tests.LexiconPluginTest1.test_cancel_create_new_entry"
#    tests = "pylucid_plugins.lexicon.tests.LexiconPluginTest1.test_error_handling"

    from pylucid_project.tests import run_test_directly
    run_test_directly(tests,
        verbosity=2,
#        failfast=True
    )
    sys.exit()


from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageContent
from pylucid_project.apps.pylucid.markup import MARKUP_CREOLE, MARKUP_HTML

from pylucid_project.pylucid_plugins.lexicon.models import LexiconEntry


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
        'Leave a comment</a>', # comments
    )
    ENTRY_MUST_CONTAIN_DE = (
        '<a href="/de/lexicon/detail/PyLucid CMS/" title="PyLucid CMS', # breadcrumbs
        '<dd>PyLucid CMS</dd>',
        '<dt>Kurzdefinition:</dt>',
        '<p>Diese Seiten werden mit PyLucid CMS generiert ;)</p>',
        'Kommentar hinterlassen</a>', # comments
    )
    ENTRY_MUST_CONTAIN_ES = (
        '<a href="/es/lexicon/detail/Spanish/" title="Spanish: Spanish is a language ;)"', # breadcrumbs
        '<dd>Spanish</dd>',
        '<p>Spanish or Castilian (español or castellano) is a Romance language...</p>',
        'Leave a comment</a>', # comments
    )

    def assertLexiconPage(self, response, must_contain):
        self.assertStatusCode(response, 200)
        self.assertResponse(response, must_contain=must_contain,
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
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
        TODO!
        Request german language entry, but english is current language
        -> redirect to english url
        """
        response = self.client.get(
            ENTRY_URL % self.other_language.code,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertRedirect(
            response, url="http://testserver" + ENTRY_URL % self.default_language.code, status_code=302
        )

    def test_get_view(self):
        response = self.client.get("/en/welcome/?lexicon=PyLucid CMS")
        self.assertResponse(response,
            must_contain=(
                'PyLucid CMS',
                'lang="en"',
                '<a href="/en/lexicon/">&lt;&lt; goto lexicon summary page</a>',
                '<dt>Short definition:</dt>',
                '<p>This pages are created by PyLucid ;)</p>',
                'Leave a comment</a>',
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )

    def test_create_csrf_error(self):
        self.login("superuser")
        csrf_client = Client(enforce_csrf_checks=True)
        url = reverse("Lexicon-new_entry")
        response = csrf_client.post(url)
        self.assertResponse(response,
            must_contain=(
                "CSRF verification failed."
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_create_form(self):
        self.login("superuser")
        url = reverse("Lexicon-new_entry")
        response = self.client.get(url)

        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        csrf_token = csrf_cookie.value

        # XXX: work-a-round for: https://github.com/gregmuellegger/django/issues/1
        response.content = response.content.replace(
            """.html('<h2 class="noanchor">loading...</h2>');""",
            """.html('loading...');"""
        )
        self.assertDOM(response,
            must_contain=(
                "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % csrf_token,
                '<input id="id_term" maxlength="255" name="term" type="text" />',
                '<textarea cols="40" id="id_content" name="content" rows="10"></textarea>',
                '<input type="submit" name="save" value="Save" />',
            ),
        )
        self.assertResponse(response,
            must_contain=(
                "<title>PyLucid - Create a new lexicon entry</title>",
                '<form', 'action="%s"' % url,
            ),
            must_not_contain=("Traceback", "Form errors", "field is required",
                "XXX INVALID TEMPLATE STRING"
            )
        )

    def test_create_new_entry(self):
        self.login("superuser")
        url = reverse("Lexicon-new_entry")
        response = self.client.post(url, data={
            'content': '**foo** //bar//',
            'is_public': 'on',
            'language': 1,
            'markup': 6,
            'short_definition': 'jojo',
            'sites': 1,
            'term': 'test'},
            follow=True,
        )
        self.assertResponse(response,
            must_contain=(
                "<title>PyLucid CMS - The &#39;lexicon&#39; plugin page.</title>",
                '<dt>Term:</dt>', '<dd>test</dd>',
                '<dt>Short definition:</dt>', '<dd>jojo</dd>',
                '<dt>Content:</dt>', '<p><strong>foo</strong> <i>bar</i></p>',
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )

    def test_cancel_create_new_entry(self):
        self.login("superuser")
        url = reverse("Lexicon-new_entry")
        response = self.client.post(url, data={"cancel": "Cancel"}, follow=True)
        self.assertResponse(response,
            must_contain=(
                "Create new lexicon entry aborted, ok.",
                "<title>PyLucid CMS - The &#39;lexicon&#39; plugin page.</title>",
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )

    def test_create_new_entry_preview(self):
        self.login("superuser")
        url = reverse("Lexicon-markup_preview")
        response = self.client.post(url, data={
            'content': '**foo** //bar//',
            'markup': 6,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True,
        )
        self.assertResponse(response,
            must_contain=(
                '<p><strong>foo</strong> <i>bar</i></p>',
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING", "<body", "<html")
        )

    def test_error_handling(self):
        self.login("staff")

        pagecontent = PageContent.objects.all().filter(markup=MARKUP_HTML)[0]

        url = pagecontent.get_absolute_url()

        pagecontent.content = "<p>\nDoes PyLucid rocks?\n</p>"
        pagecontent.save()

        # Check unmodified page
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS',
                '''<a href="?lexicon=PyLucid CMS" title="lexicon entry 'PyLucid CMS' - PyLucid is the CMS thats built this page." class="PyLucidPlugins lexicon openinwindow">PyLucid</a> rocks?''',

            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )

        pagecontent.content += "\n<p>This is not <a error 0=0> html, isn't it?</p>\n"
        pagecontent.save()

        settings.DEBUG = False # don't raise traceback

        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS',
                'Wrong HTML code (malformed start tag, at line 4, column 25)',
                '''<pre>&lt;p&gt;This is not &lt;a error 0=0&gt; html, isn't it?&lt;/p&gt;''',
                '------------------------^</pre>',
                'Does PyLucid rocks?',
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
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
            "markup": MARKUP_CREOLE,
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


