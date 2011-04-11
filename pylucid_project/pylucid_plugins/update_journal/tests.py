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
from django.test.client import Client
from django.core.urlresolvers import reverse

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PluginPage, PageContent



class UpdateJournalTest(basetest.BaseLanguageTestCase):
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
        super(UpdateJournalTest, self)._pre_setup(*args, **kwargs)

        plugin_page = PluginPage.objects.get(app_label="pylucid_project.pylucid_plugins.update_journal")
        self.feed_base_url = plugin_page.pagetree.get_absolute_url()

    def test_select_page(self):
        """ Simply test if we get the find&replace form as a superuser. """
        language_code = self.default_language.code
        url = "/%s%s" % (language_code, self.feed_base_url)
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=language_code)
        self.assertResponse(response,
            must_contain=(
                "Please select syndication feed format:",
                "feed.atom", "Atom Syndication Format",
                "feed.rss", "Really Simple Syndication",
            ),
            must_not_contain=("Traceback",)
        )

    def _test_atom_feed(self, language):
        language_code = language.code
        url = "/%s%sfeed.atom" % (language_code, self.feed_base_url)
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=language_code)
        self.assertAtomFeed(response, language_code)

    def test_atom_feed_default_language(self):
        self._test_atom_feed(self.default_language)

    def test_atom_feed_other_language(self):
        self._test_atom_feed(self.other_language)

    def _test_rss_feed(self, language):
        language_code = language.code
        url = "/%s%sfeed.rss" % (language_code, self.feed_base_url)
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=language_code)
        self.assertRssFeed(response, language_code)

    def test_rss_feed_default_language(self):
        self._test_rss_feed(self.default_language)

    def test_rss_feed_other_language(self):
        self._test_rss_feed(self.other_language)



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__,
        verbosity=1,
#        verbosity=0,
        failfast=True
    )
