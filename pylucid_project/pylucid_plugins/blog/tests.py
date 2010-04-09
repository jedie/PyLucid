#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" blog entry in english and german
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.test.client import Client

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PluginPage, PageContent

from blog.models import BlogEntry


SUMMARY_URL = "/%s/blog/"
CREATE_URL = "/pylucid_admin/plugins/blog/new_blog_entry/"
ENTRY_URL = "/%s/blog/detail/PyLucid CMS/"
ADD_PERMISSION = "blog.add_blogentry"


class BlogPluginTestCase(basetest.BaseLanguageTestCase):
    """
    inherited from BaseUnittest:
        - assertPyLucidPermissionDenied()
        - initial data fixtures with default test users
        - self.login()
    
    inherited from BaseLanguageTest:
        - self.default_language - system default Language model instance (default: en instance)
        - self.other_lang_code - alternative language code than system default (default: 'de')
        - self.other_language - alternative Language mode instance (default: de instance)
        - assertContentLanguage() - Check if response is in right language
    """
    SUMMARY_MUST_CONTAIN_EN = (
        '<a href="/en/blog/" title="Your personal weblog.">blog</a>',
        '<a href="/en/blog/">All blog articles in English.</a>',
    )
    SUMMARY_MUST_CONTAIN_DE = (
        '<a href="/de/blog/" title="Dein eigener Weblog.">blog</a>',
        '<a href="/de/blog/">Alle Blog Artikel in Deutsch.</a>',
    )
    ENTRY_MUST_CONTAIN_EN = (
        '<a href="/en/blog/detail/PyLucid CMS/" title="PyLucid CMS', # breadcrumbs
        '<dd>PyLucid CMS</dd>',
        '<dt>Short definition:</dt>',
        '<p>This pages are created by PyLucid ;)</p>',
        '<legend>Leave a comment</legend>', # comments
    )
    ENTRY_MUST_CONTAIN_DE = (
        '<a href="/de/blog/detail/PyLucid CMS/" title="PyLucid CMS', # breadcrumbs
        '<dd>PyLucid CMS</dd>',
        '<dt>Kurzdefinition:</dt>',
        '<p>Diese Seiten werden mit PyLucid CMS generiert ;)</p>',
        '<legend>Leave a comment</legend>', # comments
    )

    def assertBlogPage(self, response, must_contain):
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response, must_contain=must_contain,
            must_not_contain=("Traceback",)
        )

    def assertSummaryEN(self, response):
        self.assertBlogPage(response, must_contain=self.SUMMARY_MUST_CONTAIN_EN)

    def assertSummaryDE(self, response):
        self.assertBlogPage(response, must_contain=self.SUMMARY_MUST_CONTAIN_DE)

    def assertEntryEN(self, response):
        self.assertBlogPage(response, must_contain=self.ENTRY_MUST_CONTAIN_EN)

    def assertEntryDE(self, response):
        self.assertBlogPage(response, must_contain=self.ENTRY_MUST_CONTAIN_DE)

    def login_with_blog_add_permissions(self):
        """ login as normal user and add 'blog add permissions' """
        return self.login_with_permissions(usertype="normal", permissions=(ADD_PERMISSION,))


class BlogPluginAnonymousTest(BlogPluginTestCase):
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

    def test_login_before_create(self):
        """ Anonymous user must login, to create new blog articles """
        response = self.client.get(CREATE_URL)
        self.assertRedirect(response,
            url="http://testserver/?auth=login&next_url=/pylucid_admin/plugins/blog/new_blog_entry/",
            status_code=302
        )



class BlogPluginTest(BlogPluginTestCase):
    """
    Test with a user witch are logged in and has ADD_PERMISSION
    """
    def setUp(self):
        self.client = Client() # start a new session

    def test__normal_user_without_permissions(self):
        """ test with insufficient permissions: normal, non-stuff user """
        self.login("normal")
        response = self.client.get(CREATE_URL)
        self.assertPyLucidPermissionDenied(response)

    def test_staff_user_without_permissions(self):
        """ test with insufficient permissions: staff user without any permissions """
        self.login("staff")
        response = self.client.get(CREATE_URL)
        self.assertPyLucidPermissionDenied(response)

    def test_create_page(self):
        """
        get the create page, with normal user witch has the add permission
        """
        self.login_with_blog_add_permissions()
        response = self.client.get(CREATE_URL)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - Create a new blog entry</title>',
                'form action="%s"' % CREATE_URL,
                'input type="submit" name="save" value="save"',
                'textarea id="id_content"',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_create_entry(self):
        self.login_with_blog_add_permissions()
        response = self.client.post(CREATE_URL, data={
            "headline": "The blog headline",
            "content": "The **blog article content** in //creole// markup!",
            "markup": PageContent.MARKUP_CREOLE,
            "is_public": "on",
            "language": self.default_language.id,
            "sites": settings.SITE_ID,
            "tags": "django-tagging, tag1, tag2",
        })
        blog_article_url = "http://testserver/en/blog/1/the-blog-headline/"
        self.assertRedirect(response, url=blog_article_url, status_code=302)


class BlogPluginArticleTest(BlogPluginTestCase):
    """
    Test blog plugin with existing blog articles in different languages
    """
    def _pre_setup(self, *args, **kwargs):
        """ create some blog articles """
        super(BlogPluginArticleTest, self)._pre_setup(*args, **kwargs)

        defaults = {
            "markup": PageContent.MARKUP_CREOLE,
            "is_public": True,
        }

        self.entry_en1 = self.easy_create(BlogEntry, defaults,
            headline="First entry in english",
            content="1. **blog article** in //english//!",
            language=self.default_language,
            tags="sharedtag, first_tag, english-tag",
        )

        self.entry_en2 = self.easy_create(BlogEntry, defaults,
            headline="Second entry in english",
            content="2. **blog article** in //english//!",
            language=self.default_language,
            tags="sharedtag, second_tag, english-tag",
        )

        self.entry_de1 = self.easy_create(BlogEntry, defaults,
            headline="Erster Eintrag in deutsch",
            content="1. **Blog Artikel** in //deutsch//!",
            language=self.other_language,
            tags="sharedtag, erster_tag, deutsch-tag",
        )

        self.entry_de2 = self.easy_create(BlogEntry, defaults,
            headline="Zweiter Eintrag in deutsch",
            content="2. **Blog Artikel** in //deutsch//!",
            language=self.other_language,
            tags="sharedtag, zweiter_tag, deutsch-tag",
        )

    def assertSecondAticle(self, response):
        self.assertContentLanguage(response, self.default_language)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - Second entry in english</title>',

                '<a href="/en/blog/2/second-entry-in-english/" class="blog_headline"'
                ' hreflang="en">Second entry in english</a>',

                '<a href="/en/blog/2/second-entry-in-english/"'
                ' title="Blog article &#39;Second entry in english&#39;">Second entry in english</a>',

                # english tag cloud:
                'tag cloud', '<a href="/en/blog/tags/english-tag/" style="font-size:2em;">english-tag</a>',

                'class="content" lang="en"><p>2. <strong>blog article</strong> in <i>english</i>!</p>',

                "entry in english", "first_tag", "english-tag",

                # from comments contrib:
                'Leave a comment', '<textarea id="id_comment"', 'csrfmiddlewaretoken',
            ),
            must_not_contain=("Traceback",
                # Not the summary page:
                "All blog articles", "Alle Blog Artikel",

                # not the german tag cloud:
                'Tag Cloud', '<a href="/en/blog/tags/deutsch-tag/" style="font-size:2em;">deutsch-tag</a>',
            )
        )

    def test_absolute_url(self):
        self.failUnlessEqual(self.entry_en1.get_absolute_url(), "/en/blog/1/first-entry-in-english/")
        self.failUnlessEqual(self.entry_de1.get_absolute_url(), "/de/blog/3/erster-eintrag-in-deutsch/")

    def test_summary_en(self):
        """ test the summary page in english """
        response = self.client.get(
            SUMMARY_URL % self.default_language.code,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertSummaryEN(response)
        self.assertContentLanguage(response, self.default_language)
        self.assertResponse(response,
            must_contain=(
                'All blog articles in English.',
                '<a href="/en/blog/1/first-entry-in-english/"',
                'First entry in english',
                '<a href="/en/blog/2/second-entry-in-english/"',
                'Second entry in english',
                '<p>1. <strong>blog article</strong> in <i>english</i>!</p>',
                '<p>2. <strong>blog article</strong> in <i>english</i>!</p>',

                # from django-tagging:
                'tag cloud',
                '<a href="/en/blog/tags/english-tag/" style="font-size:2em;">english-tag</a>',
                '<a href="/en/blog/tags/first_tag/" style="font-size:1em;">first_tag</a>',
                '<a href="/en/blog/tags/second_tag/" style="font-size:1em;">second_tag</a>',
                '<a href="/en/blog/tags/sharedtag/" style="font-size:2em;">sharedtag</a>',
            ),
            must_not_contain=("Traceback",
                "Eintrag in deutsch",
                "erster_tag", "deutsch-tag"
                # from comments contrib:
                'Leave a comment', '<textarea id="id_comment"', 'csrfmiddlewaretoken',
            )
        )

    def test_summary_de(self):
        """ test the summary page in deutsch """
        response = self.client.get(
            SUMMARY_URL % self.other_language.code,
            HTTP_ACCEPT_LANGUAGE=self.other_language.code,
        )
        self.assertSummaryDE(response)
        self.assertContentLanguage(response, self.other_language)
        self.assertResponse(response,
            must_contain=(
                'Alle Blog Artikel in Deutsch.',
                '<a href="/de/blog/3/erster-eintrag-in-deutsch/"',
                'Erster Eintrag in deutsch',
                '<a href="/de/blog/4/zweiter-eintrag-in-deutsch/"',
                'Zweiter Eintrag in deutsch',
                '<p>1. <strong>Blog Artikel</strong> in <i>deutsch</i>!</p>',
                '<p>2. <strong>Blog Artikel</strong> in <i>deutsch</i>!</p>',

                # from django-tagging:
                'Tag Cloud',
                '<a href="/de/blog/tags/deutsch-tag/" style="font-size:2em;">deutsch-tag</a>',
                '<a href="/de/blog/tags/erster_tag/" style="font-size:1em;">erster_tag</a>',
                '<a href="/de/blog/tags/sharedtag/" style="font-size:2em;">sharedtag</a>',
                '<a href="/de/blog/tags/zweiter_tag/" style="font-size:1em;">zweiter_tag</a>',
            ),
            must_not_contain=("Traceback",
                "entry in english",
                "first_tag", "english-tag"
                # from comments contrib:
                'Leave a comment', '<textarea id="id_comment"', 'csrfmiddlewaretoken',
            )
        )

    def test_update_journal(self):
        # Check if listed in update journal
        response = self.client.get("/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<td>blog entry</td>',
                '<a href="/de/blog/4/zweiter-eintrag-in-deutsch/">Zweiter Eintrag in deutsch</a>',
                '<a href="/de/blog/3/erster-eintrag-in-deutsch/">Erster Eintrag in deutsch</a>',
                '<a href="/en/blog/2/second-entry-in-english/">Second entry in english</a>',
                '<a href="/en/blog/1/first-entry-in-english/">First entry in english</a>',
            ),
            must_not_contain=("Traceback",)
        )

    def test_second_entry(self):
        """ request the second, english entry. """
        response = self.client.get(
            "/en/blog/2/second-entry-in-english/",
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertSecondAticle(response)

    def test_second_entry_as_german(self):
        """
        request the second, english entry, with http accept in german.
        The blog plugin switches to english.
        """
        # The first request activae german language from http accept
        # But the blog article is written in english. PyLucid changed
        # the language in url and cookie and redirect
        response = self.client.get(
            "/de/blog/2/second-entry-in-english/",
            HTTP_ACCEPT_LANGUAGE=self.other_language.code,
        )
        self.assertRedirect(
            response, url="http://testserver/en/blog/2/second-entry-in-english/", status_code=301
        )

        # 'Follow' the redirection and get the page and article in english
        response = self.client.get(
            "/en/blog/2/second-entry-in-english/",
            HTTP_ACCEPT_LANGUAGE=self.other_language.code,
        )
        self.assertSecondAticle(response)




if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
#    management.call_command('test', "pylucid_plugins.blog.tests.BlogPluginArticleTest",
#        verbosity=0,
##        verbosity=1,
#        failfast=True
#    )
    management.call_command('test', __file__,
        verbosity=1,
#        verbosity=0,
#        failfast=True
    )
