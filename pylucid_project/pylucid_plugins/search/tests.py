#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
    
    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings

from pylucid_project.tests.test_tools.basetest import BaseUnittest

from pylucid_project.pylucid_plugins.search.preference_forms import SearchPreferencesForm


class SearchTest(BaseUnittest):

    def test_search(self):
        response = self.client.post("/en/welcome/?search=", data={"search": "PyLucid"})
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - Advanced search</title>',
                "<input type='hidden' name='csrfmiddlewaretoken' value='",
                '<input type="hidden" name="search_page" value="true" >',
                'value="PyLucid"', 'id="id_search"',
                '<input type="submit" value="search" />',
                'Search Form',
                'Search results',
                "Search in ", " plugins",
                "duration: ", "sec.",
                "hits: ",
                '<strong>PyLucid</strong>',
            ),
            must_not_contain=(
                "Traceback", "XXX INVALID TEMPLATE STRING",
                "Form errors", "field is required",
                "comments",
            )
        )

    def test_short_terms(self):
        response = self.client.post("/en/welcome/?search=", data={"search": "py foo bar"})
        self.assertStatusCode(response, 200)

        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        csrf_token = csrf_cookie.value
        self.assertDOM(response,
            must_contain=(
                '<title>PyLucid CMS - Advanced search</title>',
                "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % csrf_token,
                '<input type="hidden" name="search_page" value="true" >',
                '<input autofocus="autofocus" id="id_search" name="search" required="required" type="text" value="py foo bar" />',
                '<input type="submit" value="search" />',
            )
        )
        self.assertResponse(response,
            must_contain=(
                "Ignore &#39;py&#39; (too small)",
                'Search Form',
                'Search results',
                "Search in ", " plugins",
                "duration: ", "sec.",
                "hits: ",
            ),
            must_not_contain=(
                "Traceback", "XXX INVALID TEMPLATE STRING",
                "Form errors", "field is required"
            )
        )

    def test_no_search_term_left(self):
        response = self.client.post("/en/welcome/?search=", data={"search": "py xy z"})
        self.assertStatusCode(response, 200)

        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        csrf_token = csrf_cookie.value
        self.assertDOM(response,
            must_contain=(
                '<title>PyLucid CMS - Advanced search</title>',
                "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % csrf_token,
                '<input type="hidden" name="search_page" value="true" >',
                '<input autofocus="autofocus" id="id_search" name="search" required="required" type="text" value="py xy z" />',
                '<input type="submit" value="search" />',
            )
        )
        self.assertResponse(response,
            must_contain=(
                "Ignore &#39;py&#39; (too small)",
                "Ignore &#39;xy&#39; (too small)",
                "Ignore &#39;z&#39; (too small)",
                "Error: no search term left, can&#39;t search",
                'Search Form',
            ),
            must_not_contain=(
                "Traceback", "XXX INVALID TEMPLATE STRING",
                "Form errors", "field is required"
                'Search results',
                "Search in ", " plugins",
                "duration: ", "sec.",
                "hits: ",
            )
        )



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    tests = __file__
#    tests = "pylucid_plugins.search.tests.SearchTest.test_prefered_language"

    management.call_command('test', tests,
        verbosity=2,
#        failfast=True
    )
