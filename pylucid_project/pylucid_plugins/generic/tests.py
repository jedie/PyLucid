#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
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


class GenericTest(basetest.BaseLanguageTestCase):
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
        super(GenericTest, self)._pre_setup(*args, **kwargs)

        pagetree = PageTree.objects.get_root_page(user=AnonymousUser())
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

    def test_youtube_basic(self):
        self._test(
            '{% lucidTag generic.youtube id="-VideoID-" %}',
            must_contain=(
                '<object width="640" height="505">',
                '<param name="movie" value="http://www.youtube.com/v/-VideoID-?fs=1&amp;hd=1&amp;rel=0&amp;hl=en"></param>',
                '<embed src="http://www.youtube.com/v/-VideoID-?fs=1&amp;hd=1&amp;rel=0&amp;hl=en" type="application/x-shockwave-flash"',
            )
        )

    def test_youtube_change_resolution(self):
        self._test(
            '{% lucidTag generic.youtube id="-FooBarID-" width=960 height=745 %}',
            must_contain=(
                '<object width="960" height="745">',
                '<param name="movie" value="http://www.youtube.com/v/-FooBarID-?fs=1&amp;hd=1&amp;rel=0&amp;hl=en"></param>',
                '<embed src="http://www.youtube.com/v/-FooBarID-?fs=1&amp;hd=1&amp;rel=0&amp;hl=en" type="application/x-shockwave-flash"',
            )
        )

    def test_ohloh_basic(self):
        self._test(
            '{% lucidTag generic.ohloh project="pylucid" %}',
            must_contain=(
                '<script type="text/javascript" src="http://www.ohloh.net/p/pylucid/widgets/project_thin_badge.js"></script>'
            )
        )

    def test_ohloh_change_js_file(self):
        self._test(
            '{% lucidTag generic.ohloh project="python" js_file="project_users.js?style=rainbow" %}',
            must_contain=(
                '<script type="text/javascript" src="http://www.ohloh.net/p/pylucid/widgets/project_users.js?style=rainbow"></script>'
            )
        )


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
#    management.call_command('test', "pylucid_plugins.page_admin.tests.ConvertMarkupTest",
##        verbosity=0,
#        verbosity=1,
#        failfast=True
#    )
    management.call_command('test', __file__,
        verbosity=2,
#        failfast=True
    )
