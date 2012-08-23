#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" blog entry in english and german
    
    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


import os
import sys
import datetime


if __name__ == "__main__":
    # Run all unittest directly

    tests = __file__
#    tests = "pylucid_plugins.blog.tests.BlogPluginCsrfTest"
#    tests = "pylucid_plugins.blog.tests.BlogPluginAnonymousTest"
#    tests = "pylucid_plugins.blog.tests.BlogPluginTagsTest"
#    tests = "pylucid_plugins.blog.tests.BlogLanguageFilterTest"
#    tests = "pylucid_plugins.blog.tests.BlogPluginTest"
#    tests = "pylucid_plugins.blog.tests.BlogPluginTest.test_cancel_edit_entry"
#    tests = "pylucid_plugins.blog.tests.BlogPluginTest.test_url_date"
#    tests = "pylucid_plugins.blog.tests.BlogPluginTest.test_create_csrf_check"
#    tests = "pylucid_plugins.blog.tests.BlogPluginTest.test_creole_markup"
#    tests = "pylucid_plugins.blog.tests.BlogPluginArticleTest"

    from pylucid_project.tests import run_test_directly
    run_test_directly(tests,
        verbosity=2,
#        failfast=True,
        failfast=False,
    )
    sys.exit()


from django.conf import settings
from django.contrib.messages import constants as message_constants
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.test.client import Client

from django_tools.unittest_utils.BrowserDebug import debug_response

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.markup import MARKUP_CREOLE

from blog.models import DEBUG_LANG_FILTER, BlogEntry
from blog.preference_forms import BlogPrefForm


SUMMARY_URL = "/%s/blog/"
TAG_URL = "/%s/blog/tags/%s/"
CREATE_URL = "/pylucid_admin/plugins/blog/new_blog_entry/"
EDIT_URL = "/pylucid_admin/plugins/blog/edit/%i/"
TRANSLATE_URL = "/pylucid_admin/plugins/blog/translate/%i/"
ENTRY_URL = "/%s/blog/detail/PyLucid CMS/"
ADD_PERMISSION = "blog.add_blogentry"
BLOG_UNITTEST_FIXTURES = os.path.join(settings.PYLUCID_BASE_PATH, "pylucid_plugins", "blog", "test_fixtures.json")

TODAY_URL_PART = datetime.date.today().strftime("%Y/%m/%d")
TEST_DATE = "2000/01/24" # Date in test fixtures


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
    def _pre_setup(self, *args, **kwargs):
        self.fixtures.append(BLOG_UNITTEST_FIXTURES)
        super(BlogPluginTestCase, self)._pre_setup(*args, **kwargs)
        settings.DEBUG = False

    # existing english entries from test fixtures:
    FIRST_ENTRY = (
        "First entry in english",
        "/en/blog/%s/first-entry-in-english/" % TEST_DATE,
        "<p>1. <strong>blog article</strong> in <i>english</i>!</p>",
    )
    SECOND_ENTRY = (
        "Second entry only in english",
        "/en/blog/%s/second-entry-only-in-english/" % TEST_DATE,
        "<p>2. <strong>blog article</strong> only in <i>english</i>!</p>",
    )

    # existing german entries from test fixtures:
    ERSTER_EINTRAG = (
        "Erster Eintrag in deutsch",
        "/de/blog/%s/erster-eintrag-in-deutsch/" % TEST_DATE,
        "<p>1. <strong>Blog Artikel</strong> in <i>deutsch</i>!</p>"
    )
    DRITTER_EINTRAG = (
        "Dritter Eintrag nur in deutsch",
        "/de/blog/%s/dritter-eintrag-nur-in-deutsch/" % TEST_DATE,
        "<p>3. <strong>Blog Artikel</strong> nur in <i>deutsch</i>!</p>"
    )

    SUMMARY_EN_CONTAINS = (
        '<a href="/en/blog/" title="Your personal weblog.">blog</a>',
        '<a href="/en/blog/">All articles.</a>',
        "comments for 'blog':", "Leave a comment</a>", # from pylucid comments

    )
    SUMMARY_DE_CONTAINS = (
        '<a href="/de/blog/" title="Dein eigener Weblog.">blog</a>',
        '<a href="/de/blog/">Alle Artikel.</a>',
        "Kommentare für 'blog':", "Kommentar hinterlassen</a>", # from pylucid comments
    )

    ENTRY_MUST_CONTAIN_EN = (
        '<a href="/en/blog/detail/PyLucid CMS/" title="PyLucid CMS', # breadcrumbs
        '<dd>PyLucid CMS</dd>',
        '<dt>Short definition:</dt>',
        '<p>This pages are created by PyLucid ;)</p>',
        'Leave a comment</a>', # from pylucid comments
    )
    ENTRY_MUST_CONTAIN_DE = (
        '<a href="/de/blog/detail/PyLucid CMS/" title="PyLucid CMS', # breadcrumbs
        '<dd>PyLucid CMS</dd>',
        '<dt>Kurzdefinition:</dt>',
        '<p>Diese Seiten werden mit PyLucid CMS generiert ;)</p>',
        'Leave a comment</a>', # from pylucid comments
    )

    def assertBlogPage(self, response, language, must_contain, must_not_contain):
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response, must_contain=must_contain,
            must_not_contain=must_not_contain + ("Traceback", "XXX INVALID TEMPLATE STRING")
        )
        self.assertContentLanguage(response, language)

#    def assertSummaryEN(self, response):
#        self.assertBlogPage(response,
#            must_contain=self.SUMMARY_MUST_CONTAIN_EN,
#            must_not_contain=self.SUMMARY_MUST_NOT_CONTAIN_EN,
#        )
#
#    def assertSummaryDE(self, response):
#        self.assertBlogPage(response,
#            must_contain=self.SUMMARY_MUST_CONTAIN_DE,
#            must_not_contain=self.SUMMARY_MUST_NOT_CONTAIN_DE,
#        )

    def assertEntryEN(self, response):
        self.assertBlogPage(response, must_contain=self.ENTRY_MUST_CONTAIN_EN)

    def assertEntryDE(self, response):
        self.assertBlogPage(response, must_contain=self.ENTRY_MUST_CONTAIN_DE)

    def login_with_blog_add_permissions(self):
        """ login as normal user and add 'blog add permissions' """
        return self.login_with_permissions(usertype="normal", permissions=(ADD_PERMISSION,))


class BlogPluginAnonymousTestCase(BlogPluginTestCase):
    def setUp(self):
        cache.clear()

        from pylucid_project.apps.pylucid.preference_forms import SystemPreferencesForm
        self.system_pref_form = SystemPreferencesForm()
        self.system_preferences = self.system_pref_form.get_preferences()
        self.system_preferences["message_level_anonymous"] = message_constants.DEBUG
        self.system_pref_form.save()

        DEBUG_LANG_FILTER = True
        settings.PYLUCID.I18N_DEBUG = True

        self.pref_form = BlogPrefForm()

    def _set_language_filter(self, language_filter):
        self.pref_form["language_filter"] = language_filter
        self.pref_form.save()


class BlogPluginAnonymousTest(BlogPluginAnonymousTestCase):
    """
    ALL_LANGUAGES - "Don't filter by languages. Allways display all blog entries."
    PREFERED_LANGUAGES - "Filter by client prefered languages (set in browser and send by HTTP_ACCEPT_LANGUAGE header)"
    CURRENT_LANGUAGE - "Display only blog entries in current language (select on the page)"
    """
    def test_summary_en_all_languages(self):
        self._set_language_filter(BlogPrefForm.ALL_LANGUAGES)

        response = self.client.get(
            SUMMARY_URL % self.default_language.code,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertBlogPage(response, self.default_language,
            must_contain=self.SUMMARY_EN_CONTAINS + self.FIRST_ENTRY + self.SECOND_ENTRY + self.DRITTER_EINTRAG,
            must_not_contain=self.SUMMARY_DE_CONTAINS + self.ERSTER_EINTRAG,
        )

    def test_summary_en_current_languages(self):
        self._set_language_filter(BlogPrefForm.CURRENT_LANGUAGE)

        response = self.client.get(
            SUMMARY_URL % self.default_language.code,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertBlogPage(response, self.default_language,
            must_contain=self.SUMMARY_EN_CONTAINS + self.FIRST_ENTRY + self.SECOND_ENTRY,
            must_not_contain=self.SUMMARY_DE_CONTAINS + self.ERSTER_EINTRAG + self.DRITTER_EINTRAG,
        )

    def test_summary_robots(self):
        self._set_language_filter(BlogPrefForm.ALL_LANGUAGES)

        response = self.client.get(
            SUMMARY_URL % self.default_language.code,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertBlogPage(response, self.default_language,
            must_contain=('<meta name="robots" content="noindex,follow" />',),
            must_not_contain=(
                '<meta name="robots" content="index,follow" />',
                '<meta name="robots" content="noindex,nofollow" />',
            )
        )

    def test_tag_view_robots(self):
        self._set_language_filter(BlogPrefForm.ALL_LANGUAGES)

        url = TAG_URL = "/%s/blog/tags/%s/" % (self.default_language.code, "deutsch-tag")
        response = self.client.get(url,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertBlogPage(response, self.default_language,
            must_contain=('<meta name="robots" content="noindex,nofollow" />',),
            must_not_contain=('<meta name="robots" content="index,follow" />',)
        )

    def test_same_slug_en(self):
        self._set_language_filter(BlogPrefForm.ALL_LANGUAGES)

        lang_code = self.default_language.code
        url = "%s%s/same-slug/" % (SUMMARY_URL % lang_code, TEST_DATE)

        response = self.client.get(url,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertBlogPage(response, self.default_language,
            must_contain=(
                '<html lang="en">',
                "Same headline in german and english",
                "<p>4. <strong>blog article</strong> in <i>english</i>!</p>",
            ),
            must_not_contain=("Traceback",),
        )

    def test_same_slug_de(self):
        self._set_language_filter(BlogPrefForm.ALL_LANGUAGES)

        lang_code = self.other_language.code
        url = "%s%s/same-slug/" % (SUMMARY_URL % lang_code, TEST_DATE)

        response = self.client.get(url,
            HTTP_ACCEPT_LANGUAGE=self.other_language.code,
        )
        self.assertBlogPage(response, self.other_language,
            must_contain=(
                '<html lang="de">',
                "Same headline in german and english",
                "<p>4. <strong>Blog Artikel</strong> in <i>deutsch</i>!</p>",
            ),
            must_not_contain=("Traceback",),
        )

    def test_login_before_edit(self):
        """ Anonymous user must login, to edit a existing blog article """
        url = EDIT_URL % 1
        response = self.client.get(url)
        self.assertRedirect(response,
            url="http://testserver/?auth=login&next_url=%s" % url,
            status_code=302
        )

#    def test_summary_en_prefered_languages(self):
#        self._set_language_filter(BlogPrefForm.PREFERED_LANGUAGES)
#
#        response = self.client.get(
#            SUMMARY_URL % self.default_language.code,
#            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
#        )
#        self.assertBlogPage(response, self.default_language,
#            must_contain=self.SUMMARY_EN_CONTAINS + self.FIRST_ENTRY + self.SECOND_ENTRY,
#            must_not_contain=self.SUMMARY_DE_CONTAINS + self.ERSTER_EINTRAG + self.DRITTER_EINTRAG,
#        )
#
#        response = self.client.get(
#            SUMMARY_URL % self.default_language.code,
#            HTTP_ACCEPT_LANGUAGE=";".join([self.default_language.code, self.other_language]),
#        )
#        self.assertBlogPage(response, self.default_language,
#            must_contain=self.SUMMARY_EN_CONTAINS + self.FIRST_ENTRY + self.SECOND_ENTRY + self.DRITTER_EINTRAG,
#            must_not_contain=self.SUMMARY_DE_CONTAINS + self.ERSTER_EINTRAG,
#        )

'''
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
            url="http://testserver/?auth=login&next_url=%s" % CREATE_URL,
            status_code=302
        )

    def test_login_before_translate(self):
        """ Anonymous user must login, to translate a blog article """
        url = TRANSLATE_URL % 1
        response = self.client.get(url)
        self.assertRedirect(response,
            url="http://testserver/?auth=login&next_url=%s" % url,
            status_code=302
        )

    def _test_atom_feed(self, language):
        language_code = language.code
        response = self.client.get(
            "/%s/blog/feed/feed.atom" % language_code,
            HTTP_ACCEPT_LANGUAGE=language_code,
        )
        self.assertAtomFeed(response, language_code)

    def test_atom_feed_default_language(self):
        self._test_atom_feed(self.default_language)

    def test_atom_feed_other_language(self):
        self._test_atom_feed(self.other_language)

    def _test_rss_feed(self, language):
        language_code = language.code
        response = self.client.get(
            "/%s/blog/feed/feed.rss" % language_code,
            HTTP_ACCEPT_LANGUAGE=language_code,
        )
        self.assertRssFeed(response, language_code)

    def test_rss_feed_default_language(self):
        self._test_rss_feed(self.default_language)

    def test_rss_feed_other_language(self):
        self._test_rss_feed(self.other_language)
'''

class BlogPluginTagsTest(BlogPluginAnonymousTestCase):
    """
    ALL_LANGUAGES - "Don't filter by languages. Allways display all blog entries."
    PREFERED_LANGUAGES - "Filter by client prefered languages (set in browser and send by HTTP_ACCEPT_LANGUAGE header)"
    CURRENT_LANGUAGE - "Display only blog entries in current language (select on the page)"
    """

    def setUp(self):
        super(BlogPluginTagsTest, self).setUp()

        self.pref_form["max_tag_count"] = 2 # Allow only two tag filters
        self.pref_form.save()
        self._set_language_filter(BlogPrefForm.ALL_LANGUAGES)

    def test_canonical_url(self):
        url = TAG_URL = "/%s/blog/tags/%s/" % (self.default_language.code,
            "/".join(["sharedtag", "second_tag"])
        )
        response = self.client.get(url,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertRedirect(response,
            # and not ...estserver/en/blog/tags/sharedtag/second_tag/ ;)
            url="http://testserver/en/blog/tags/second_tag/sharedtag/",
            status_code=301 # permanent redirect
        )

    def test_one_tag_filter(self):
        # With one tag filter, other tags has "add-link"
        url = TAG_URL = "/%s/blog/tags/%s/" % (self.default_language.code, "sharedtag")
        response = self.client.get(url,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertBlogPage(response, self.default_language,
            must_contain=('Your personal weblog.',
                '<strong style="font-size:2em;">sharedtag</strong>', # current tag filter
                'rel="nofollow">[+]</a>', # link to add tag filter
                'rel="nofollow">second_tag</a>', # Other tag filter
            ),
            must_not_contain=('Traceback',)
        )

    def test_reached_tag_filters(self):
        # With two tags, the max number of filters is reached -> No "add-link"
        url = TAG_URL = "/%s/blog/tags/%s/" % (self.default_language.code,
            "/".join(["second_tag", "sharedtag"])
        )
        response = self.client.get(url,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertBlogPage(response, self.default_language,
            must_contain=('Your personal weblog.',
                '<strong style="font-size:1em;">second_tag</strong>', # current tag filter 1
                '<strong style="font-size:1em;">sharedtag</strong>', # current tag filter 2
                'rel="nofollow">english-tag</a>', # Other tag filter
            ),
            must_not_contain=('Traceback',
                'rel="nofollow">[+]</a>', # link to add tag filter
            )
        )

    def test_too_mush_tags_filters(self):
        # With three tags are one to murch -> raise 404
        url = TAG_URL = "/%s/blog/tags/%s/" % (self.default_language.code,
            "/".join(["second_tag", "sharedtag", "english-tag"])
        )
        response = self.client.get(url,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.failUnlessEqual(response.status_code, 404)

    def _request_with_too_much_tags(self):
        url = TAG_URL = "/%s/blog/tags/%s/" % (self.default_language.code,
            "/".join(["second_tag", "sharedtag", "english-tag", "too_mutch"])
        )
        response = self.client.get(url,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        return response

    def test_too_mush_tags_filters_and_ban(self):
        ban_count = int(self.system_preferences["ban_count"])

        for i in xrange(ban_count):
            # With four tags are two to murch -> raise SuspiciousOperation and log this
            response = self._request_with_too_much_tags()
            self.failUnlessEqual(response.status_code, 404)

        # We are banned after 'ban_count' bad requests -> Get 403 Forbidden
        response = self._request_with_too_much_tags()
        self.failUnlessEqual(response.status_code, 403)

        # Important: We must remove "us" from ban list, otherwise other unittests
        # will failed ;)
        from pylucid_project.apps.pylucid.models import BanEntry
        BanEntry.objects.all().delete()

        # Test if we are not banned anymore:
        self.test_one_tag_filter()


class BlogPluginTest(BlogPluginTestCase):
    """
    Test with a user witch are logged in and has ADD_PERMISSION
    """
    def setUp(self):
        self.client = Client() # start a new session

    def test_normal_user_without_permissions(self):
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
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - Create a new blog entry</title>',
                'form action="%s"' % CREATE_URL,
                "<input type='hidden' name='csrfmiddlewaretoken' value='",
                'input type="submit" name="save" value="Save"',
                'input type="submit" name="cancel"',
                '<textarea id="id_content" rows="10" cols="40" name="content"></textarea>',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_create_csrf_error(self):
        self.login_with_blog_add_permissions()
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(CREATE_URL)
        self.assertResponse(response,
            must_contain=(
                "CSRF verification failed."
            ),
            must_not_contain=("Traceback", "Form errors", "field is required",

            )
        )

    def test_cancel_create_entry(self):
        self.login_with_blog_add_permissions()
        response = self.client.post(CREATE_URL, data={"cancel": "Cancel"}, follow=True)
        self.assertResponse(response,
            must_contain=(
                "Create new blog entry aborted, ok.",
                '<h2 id="page_title">Your personal weblog.</h2>',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_cancel_edit_entry(self):
        self.login("superuser")
        response = self.client.post(EDIT_URL % 1, data={"cancel": "Cancel"}, follow=True)
        self.assertResponse(response,
            must_contain=(
                "Edit blog entry aborted, ok.",
                '<h2 id="page_title">First entry in english</h2>'
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_create_entry(self):
        self.login_with_blog_add_permissions()
        response = self.client.post(CREATE_URL,
            data={
            "headline": "The blog headline",
            "content": "The **blog article content** in //creole// markup!",
            "markup": MARKUP_CREOLE,
            "is_public": "on",
            "language": self.default_language.id,
            "url_date": datetime.date.today(),
            "sites": settings.SITE_ID,
            "tags": "django-tagging, tag1, tag2",
        })
        blog_article_url = "http://testserver/en/blog/%s/the-blog-headline/" % TODAY_URL_PART
        self.assertRedirect(response, url=blog_article_url, status_code=302)

    def test_url_date(self):
        self.login_with_blog_add_permissions()
        response = self.client.post(CREATE_URL,
            data={
            "headline": "Tag der Deutschen Einheit...",
            "content": "...war am **03. Oktober 1990**.",
            "markup": MARKUP_CREOLE,
            "is_public": "on",
            "language": self.default_language.id,
            "url_date": "1990-10-03",
            "sites": settings.SITE_ID,
            "tags": "django-tagging, tag1, tag2",
        })
        blog_article_url = "http://testserver/en/blog/1990/10/03/tag-der-deutschen-einheit/"
        self.assertRedirect(response, url=blog_article_url, status_code=302)
        response = self.client.get(blog_article_url)
        self.assertDOM(response,
            must_contain=(
                '<li class="success">New blog entry &#39;Tag der Deutschen Einheit...&#39; saved.</li>',
                '<p>...war am <strong>03. Oktober 1990</strong>.</p>',
            ),
            must_not_contain=("Traceback", "field is required")
        )
        self.assertResponse(response,
            must_contain=(
                # Archive links (complete link doesn't match with assertHTML):
                '<a href="/en/blog/1990/"',
                '<a href="/en/blog/1990/10/"',
                '<a href="/en/blog/1990/10/03/"',
            ),
            must_not_contain=("Traceback", "field is required")
        )

    def test_unique_together_slug(self):
        self.login_with_blog_add_permissions()
        create_data = {
            "content": "The **blog article content** in //creole// markup!",
            "markup": MARKUP_CREOLE,
            "is_public": "on",
            "sites": settings.SITE_ID,

            # Same language + url_date and slug for both entries:
            "language": self.default_language.id,
            "url_date": datetime.date.today(),
            "slug": "foobar",
        }
        # Create first entry:
        create_data["headline"] = "unique headline one"
        response = self.client.post(CREATE_URL, data=create_data)
        blog_article_url = "http://testserver/en/blog/%s/foobar/" % TODAY_URL_PART
        self.assertRedirect(response, url=blog_article_url, status_code=302)

        # Try to create the same entry, again:
        create_data["headline"] = "unique headline two"
        response = self.client.post(CREATE_URL, data=create_data)
        self.assertResponse(response,
            must_contain=(
                "Create a new blog entry",
                "Form errors",
                "Blog entry content with this Language, URL Date and Slug already exists.",
            ),
            must_not_contain=("Traceback", "field is required")
        )
        # Stay at create page:
        self.assertEqual(response.request["PATH_INFO"], CREATE_URL)

    def test_unique_together_headline(self):
        self.login_with_blog_add_permissions()
        create_data = {
            "content": "The **blog article content** in //creole// markup!",
            "markup": MARKUP_CREOLE,
            "is_public": "on",
            "sites": settings.SITE_ID,

            # Same language + url_date and headline for both entries:
            "language": self.default_language.id,
            "url_date": datetime.date.today(),
            "headline": "always the same",
        }
        # Create first entry:
        create_data["slug"] = "unique_slug_one"
        response = self.client.post(CREATE_URL, data=create_data)
        blog_article_url = "http://testserver/en/blog/%s/unique_slug_one/" % TODAY_URL_PART
        self.assertRedirect(response, url=blog_article_url, status_code=302)

        # Try to create the same entry, again:
        create_data["slug"] = "unique_slug_two"
        response = self.client.post(CREATE_URL, data=create_data)
        self.assertResponse(response,
            must_contain=(
                "Create a new blog entry",
                "Form errors",
                "Blog entry content with this Language, URL Date and Headline already exists.",
            ),
            must_not_contain=("Traceback", "field is required")
        )
        # Stay at create page:
        self.assertEqual(response.request["PATH_INFO"], CREATE_URL)

    def test_creole_markup(self):
        self.login_with_blog_add_permissions()
        response = self.client.post(CREATE_URL, data={
            "headline": "The blog headline",
            "content": "A **//creole// markup** and a {{/image/url/pic.PNG|1 2}} nice?",
            "markup": MARKUP_CREOLE,
            "is_public": "on",
            "language": self.default_language.id,
            "url_date": datetime.date.today(),
            "sites": settings.SITE_ID,
            "tags": "django-tagging, tag1, tag2",
        })
        blog_article_url = "http://testserver/en/blog/%s/the-blog-headline/" % TODAY_URL_PART
        self.assertRedirect(response, url=blog_article_url, status_code=302)

        response = self.client.get(blog_article_url)
        #self.raise_browser_traceback(response, "TEST")
        self.assertResponse(response,
            must_contain=(
                '<p>A <strong><i>creole</i> markup</strong> and a <img src="/image/url/pic.PNG" title="1 2" alt="1 2" /> nice?</p>',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_markup_preview_ids(self):
        self.login_with_blog_add_permissions()
        response = self.client.get(CREATE_URL)
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                '<fieldset id="preview_id_content">',
                '$("#preview_id_content div")',

                '<select name="markup" id="id_markup">',
                'var markup_selector = "#id_markup";'
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_markup_preview(self):
        self.login("superuser")
        url = reverse("Blog-markup_preview")
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



'''
TODO:

class BlogPluginArticleTest(BlogPluginTestCase):
    """
    Test blog plugin with existing blog articles in different languages
    """
    def _pre_setup(self, *args, **kwargs):
        """ create some blog articles """
        super(BlogPluginArticleTest, self)._pre_setup(*args, **kwargs)



    def assertSecondArticle(self, response):
        self.assertContentLanguage(response, self.default_language)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - Second entry in english</title>',

                '<a href="/en/blog/2/second-entry-in-english/" class="blog_headline" hreflang="en">',
                'Second entry in english</a>',

                '<a href="/en/blog/2/second-entry-in-english/" title="Article &#39;Second entry in english&#39;">',
                'Second entry in english</a>',

                # english tag cloud:
                'tag cloud', '<a href="/en/blog/tags/english-tag/" style="font-size:2em;">english-tag</a>',

                'class="content" lang="en"><p>2. <strong>blog article</strong> in <i>english</i>!</p>',

                "entry in english", "first_tag", "english-tag",

                'Leave a comment</a>', # from pylucid comments
            ),
            must_not_contain=("Traceback",
                # Not the summary page:
                "All articles", "Alle Artikel",

                # not the german tag cloud:
                'Tag Cloud', '<a href="/en/blog/tags/deutsch-tag/" style="font-size:2em;">', 'deutsch-tag</a>',
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
                'All articles in English.',
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
                'Leave a comment</a>', # from pylucid comments
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
                'Alle Artikel in Deutsch.',
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
                'Leave a comment</a>', # from pylucid comments
            )
        )

    def test_update_journal_de(self):
        # Check if listed in update journal
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="de")
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                '(blog entry)',
                '<a href="/de/blog/4/zweiter-eintrag-in-deutsch/">', 'Zweiter Eintrag in deutsch</a>',
                '<a href="/de/blog/3/erster-eintrag-in-deutsch/">', 'Erster Eintrag in deutsch</a>',
            ),
            must_not_contain=("Traceback", "First entry", "Second entry")
        )

    def test_update_journal_en(self):
        # Check if listed in update journal
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                '(blog entry)',
                '<a href="/en/blog/2/second-entry-in-english/">', 'Second entry in english</a>',
                '<a href="/en/blog/1/first-entry-in-english/">', 'First entry in english</a>',
            ),
            must_not_contain=("Traceback", "Erster Eintrag", "Zweiter Eintrag")
        )

    def test_second_entry(self):
        """ request the second, english entry. """
        response = self.client.get(
            "/en/blog/2/second-entry-in-english/",
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertSecondArticle(response)

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
        self.assertSecondArticle(response)

    def test_all_languages(self):
        self.pref_form = BlogPrefForm()
        self.pref_form["language_filter"] = BlogPrefForm.ALL_LANGUAGES
        self.pref_form.save()

        response = self.client.get("/%s/blog/" % self.default_language.code,
            HTTP_ACCEPT_LANGUAGE=self.default_language.code,
        )
        self.assertResponse(response,
            must_contain=(
                'Zweiter Eintrag in deutsch',
                'Zweiter Eintrag in deutsch',
                'Second entry in english',
                'First entry in english',
            ),
            must_not_contain=("Traceback",)
        )
'''


class BlogPluginCsrfTest(BlogPluginTestCase):
    """
    Test the Cross Site Request Forgery protection in PyLucid with the Blog Plugin
    """
    def setUp(self):
        super(BlogPluginCsrfTest, self).setUp()
        settings.DEBUG = True

    def tearDown(self):
        super(BlogPluginCsrfTest, self).tearDown()
        settings.DEBUG = False

    def _get_loggedin_client(self):
        csrf_client = Client(enforce_csrf_checks=True)

        test_user = self._get_userdata("superuser")
        ok = csrf_client.login(username=test_user["username"],
                               password=test_user["password"])
        return csrf_client

    def test_create_entry_without_token(self):
        csrf_client = self._get_loggedin_client()

        response = csrf_client.post(CREATE_URL,
            data={
            "headline": "The blog headline",
            "content": "The **blog article content** in //creole// markup!",
            "markup": MARKUP_CREOLE,
            "is_public": "on",
            "language": self.default_language.id,
            "url_date": datetime.date.today(),
            "sites": settings.SITE_ID,
            "tags": "django-tagging, tag1, tag2",
        })
#        debug_response(response)
        self.assertResponse(response,
            must_contain=("Forbidden", "CSRF cookie not set."),
            must_not_contain=()
        )

    def test_create_entry_with_token(self):
        csrf_client = self._get_loggedin_client()

        # get the current csrf token
        response = csrf_client.get(CREATE_URL)
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
            ),
        )

        # create blog entry with csrf token
        response = csrf_client.post(CREATE_URL,
            data={
            "headline": "The blog headline",
            "content": "The **blog article content** in //creole// markup!",
            "markup": MARKUP_CREOLE,
            "is_public": "on",
            "language": self.default_language.id,
            "url_date": datetime.date.today(),
            "sites": settings.SITE_ID,
            "tags": "django-tagging, tag1, tag2",
            "csrfmiddlewaretoken": csrf_token
        })
#        debug_response(response)
        blog_article_url = "http://testserver/en/blog/%s/the-blog-headline/" % TODAY_URL_PART
        self.assertRedirect(response, url=blog_article_url, status_code=302)





