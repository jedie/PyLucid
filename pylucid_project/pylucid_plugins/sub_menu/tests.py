#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageTree, PageContent
from pylucid_project.apps.pylucid.markup import MARKUP_HTML


class SubMenuTest(basetest.BaseLanguageTestCase):
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
    def _pre_setup(self, *args, **kwargs):
        super(SubMenuTest, self)._pre_setup(*args, **kwargs)

        pagetree = PageTree.objects.get(slug="example-pages")
        self.pagecontent = PageContent.objects.get(
            pagemeta__pagetree=pagetree, pagemeta__language=self.default_language
        )
        self.pagecontent.markup = MARKUP_HTML
        self.url = self.pagecontent.get_absolute_url()

    def setUp(self):
        self.old_DEBUG = settings.DEBUG
        settings.DEBUG = True

    def tearDown(self):
        settings.DEBUG = self.old_DEBUG

    def _set_content(self, text):
        self.pagecontent.content = (
            "<p>%(pre)s</p>\n"
            "%(text)s\n"
            "<p>%(post)s</p>"
        ) % {
            "pre": "*" * 80,
            "text": text,
            "post": "^" * 80,
        }
        self.pagecontent.save()

    def _test(self, lucidtag, must_contain):
        self._set_content(lucidtag)
        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=must_contain,
            must_not_contain=(
                "Traceback", "XXX INVALID TEMPLATE STRING",
                "Form errors", "field is required",
            )
        )

    def test_default_example_page_content(self):
        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=(
                '<div class="PyLucidPlugins sub_menu" id="sub_menu_lucidTag">',
                '<dl>', '<dt>',
                '<a href="/en/example-pages/RSS/" hreflang="en">RSS feed test.</a>',
                '<dd>Integrade RSS news feeds into your CMS page.</dd>',
            ),
            must_not_contain=(
                "Traceback", "XXX INVALID TEMPLATE STRING",
                "Form errors", "field is required",
            )
        )

    def test_basic(self):
        self._test(
            '{% lucidTag sub_menu %}',
            must_contain=(
                '<p>********************************************************************************</p>',
                '<div class="PyLucidPlugins sub_menu" id="sub_menu_lucidTag">',
                '<li><a href="/en/example-pages/RSS/" hreflang="en" title="RSS feed test.">RSS</a></li>',
                '<li><a href="/en/example-pages/SourceCode/" hreflang="en" title="SourceCode">sourcecode</a></li>',
                '<p>^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^</p>',
            )
        )

    def test_use_title(self):
        self._test(
            '{% lucidTag sub_menu use_title=True %}',
            must_contain=(
                '<li><a href="/en/example-pages/RSS/" hreflang="en">RSS feed test.</a></li>',
                '<li><a href="/en/example-pages/SourceCode/" hreflang="en">SourceCode</a></li>',
            )
        )



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    management.call_command('test', __file__,
        verbosity=2,
#        failfast=True
    )
