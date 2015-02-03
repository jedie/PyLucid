#!/usr/bin/env python
# coding: utf-8


"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2010-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys

if __name__ == "__main__":
    # Run all unittest directly

    tests = __file__
#    tests = "pylucid_project.pylucid_plugins.unittest_plugin.tests"
#    tests = "pylucid_project.pylucid_plugins.unittest_plugin.tests.UnittestPluginCsrfTests"

    from pylucid_project.tests import run_test_directly
    run_test_directly(tests,
        verbosity=2,
#        failfast=True,
        failfast=False,
    )
    sys.exit()

from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import reverse

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PluginPage, PageContent



class FindReplaceTest(basetest.BaseLanguageTestCase):
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

    def assertInputFields(self, response, find_string, replace_string):
        self.assertDOM(response,
            must_contain=(
                '<input id="id_find_string" name="find_string" type="text" value="%s" />' % find_string,
                '<input id="id_replace_string" name="replace_string" type="text" value="%s" />' % replace_string,
            )
        )

    def test_replace_form(self):
        """ Simply test if we get the find&replace form as a superuser. """
        self.login("superuser")
        url = reverse("FindAndReplace-find_and_replace")
        response = self.client.get(url)
        self.assertDOM(response,
            must_contain=(
                '<input id="id_find_string" name="find_string" type="text" />',
                '<input id="id_replace_string" name="replace_string" type="text" />',
            )
        )
        self.assertResponse(response,
            must_contain=(
                '<form action="%s" method="post" id="find_and_replace' % url,
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )

    def test_pagecontent_replace_simulate(self):
        self.login("superuser")
        url = reverse("FindAndReplace-find_and_replace")

        find_string = "the"
        replace_string = "XXX"

        response = self.client.post(url, data={
            'find_string': find_string,
            'replace_string': replace_string,
            'content_type': 0, # PageContent
            'languages': ['de', 'en'],
            'save': 'find and replace',
            'sites': ['1'],
            'simulate': 'on'
        })
        self.assertInputFields(response, find_string, replace_string)
        self.assertResponse(response,
            must_contain=(
                '<form action="%s" method="post" id="find_and_replace' % url,
                'Simulate only, no entry changed.',
                '<legend class="pygments_code">Diff</legend>',
                '<span class="gd">-',
                '<span class="gi">+',
                '?  ', ' ^^^ ',
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )

    def test_pagecontent_replace(self):
        self.login("superuser")
        url = reverse("FindAndReplace-find_and_replace")

        find_string = "Welcome to your fesh PyLucid CMS installation"
        replace_string = "XXX replaced XXX"

        response = self.client.post(url, data={
            'find_string': find_string,
            'replace_string': replace_string,
            'content_type': 0, # PageContent
            'languages': ['de', 'en'],
            'sites': ['1'],
            'save': 'find and replace',
        })
        self.assertInputFields(response, find_string, replace_string)
        self.assertResponse(response,
            must_contain=(
                '<form action="%s" method="post" id="find_and_replace' % url,
                '<legend class="pygments_code">Diff</legend>',
                '<span class="gd">- Welcome to your fesh PyLucid CMS installation ;)</span>',
                '<span class="gi">+ XXX replaced XXX ;)</span>',
            ),
            must_not_contain=(
                "Traceback", 'Simulate only, no entry changed.',
                "XXX INVALID TEMPLATE STRING"
            )
        )
        response = self.client.get("/en/welcome/")
        self.assertResponse(response,
            must_contain=('XXX replaced XXX',),
            must_not_contain=(
                "Traceback", 'Welcome to your fesh PyLucid CMS installation',
                "XXX INVALID TEMPLATE STRING"
            )
        )

    def test_Headfiles_replace(self):
        self.login("superuser")
        url = reverse("FindAndReplace-find_and_replace")

        find_string = "page messages"
        replace_string = "XXX replaced XXX"

        response = self.client.post(url, data={
            'find_string': find_string,
            'replace_string': replace_string,
            'content_type': 3, # EditableHtmlHeadFile
            'languages': ['de', 'en'],
            'sites': ['1'],
            'save': 'find and replace',
        })
        self.assertInputFields(response, find_string, replace_string)
        self.assertResponse(response,
            must_contain=(
                '<form action="%s" method="post" id="find_and_replace' % url,
                '<legend class="pygments_code">Diff</legend>',
                '<span class="gd">-    page messages</span>',
                '<span class="gi">+    XXX replaced XXX</span>',
            ),
            must_not_contain=(
                "Traceback", 'Simulate only, no entry changed.',
                "XXX INVALID TEMPLATE STRING"
            )
        )


# if __name__ == "__main__":
#     # Run all unittest directly
#     from django.core import management
#
#     tests = __file__
# #    tests = "pylucid_plugins.find_and_replace.tests.FindReplaceTest.test_Headfiles_replace"
#
#     management.call_command('test', tests,
#         verbosity=2,
# #        failfast=True
#     )
