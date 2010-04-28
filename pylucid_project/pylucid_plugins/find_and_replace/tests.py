#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
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
    def test_replace_form(self):
        """ Simply test if we get the find&replace form as a superuser. """
        self.login("superuser")
        url = reverse("FindAndReplace-find_and_replace")
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<form action="%s" method="post" id="find_and_replace' % url,
                '<input type="text" name="find_string"',
                '<input type="text" name="replace_string"',
            ),
            must_not_contain=("Traceback",)
        )

    def test_pagecontent_replace_simulate(self):
        self.login("superuser")
        url = reverse("FindAndReplace-find_and_replace")
        response = self.client.post(url, data={
            'find_string': 'the',
            'replace_string': 'XXX',
            'content_type': 0, # PageContent
            'languages': ['de', 'en'],
            'save': 'find and replace',
            'simulate': 'on'
        })
        self.assertResponse(response,
            must_contain=(
                '<link rel="stylesheet" type="text/css" href="/headfile/pygments.css"',
                '<form action="%s" method="post" id="find_and_replace' % url,
                '<input type="text" name="find_string"',
                '<input type="text" name="replace_string"',
                'Simulate only, no entry changed.',
                '<legend class="pygments_code">Diff</legend>',
                '<span class="gd">-',
                '<span class="gi">+',
                '?  ', ' ^^^ ',
            ),
            must_not_contain=("Traceback",)
        )

    def test_pagecontent_replace(self):
        self.login("superuser")
        url = reverse("FindAndReplace-find_and_replace")
        response = self.client.post(url, data={
            'find_string': 'Welcome to your fesh PyLucid CMS installation',
            'replace_string': 'XXX replaced XXX',
            'content_type': 0, # PageContent
            'languages': ['de', 'en'],
            'save': 'find and replace',
        })
        self.assertResponse(response,
            must_contain=(
                '<link rel="stylesheet" type="text/css" href="/headfile/pygments.css"',
                '<form action="%s" method="post" id="find_and_replace' % url,
                '<input type="text" name="find_string"',
                '<input type="text" name="replace_string"',
                '<legend class="pygments_code">Diff</legend>',
                '<span class="gd">- Welcome to your fesh PyLucid CMS installation ;)</span>',
                '<span class="gi">+ XXX replaced XXX ;)</span>',
            ),
            must_not_contain=("Traceback", 'Simulate only, no entry changed.',)
        )
        response = self.client.get("/")
        self.assertResponse(response,
            must_contain=('XXX replaced XXX',),
            must_not_contain=("Traceback", 'Welcome to your fesh PyLucid CMS installation',)
        )



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__,
        verbosity=1,
#        verbosity=0,
        failfast=True
    )
