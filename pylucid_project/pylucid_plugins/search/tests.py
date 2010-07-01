#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from pylucid_project.tests.test_tools.basetest import BaseUnittest


class SearchTest(BaseUnittest):
    def test_get_search(self):
        response = self.client.get("/", data={"search": "PyLucid"})
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - Advanced search</title>',
                '<input type="text" name="search" value="PyLucid" id="id_search" />',
                '<input type="submit" value="search" />',
                'Search Form',
                'Search results',
                "Search in ", " plugins",
                "duration: ", "sec.",
                "hits: ",
                '<strong>PyLucid</strong>',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_short_terms(self):
        response = self.client.get("/", data={"search": "py foo bar"})
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - Advanced search</title>',
                "Ignore &#39;py&#39; (too small)",
                '<input type="text" name="search" value="py foo bar" id="id_search" />',
                '<input type="submit" value="search" />',
                'Search Form',
                'Search results',
                "Search in ", " plugins",
                "duration: ", "sec.",
                "hits: ",
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_no_search_term_left(self):
        response = self.client.get("/", data={"search": "py xy z"})
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - Advanced search</title>',
                "Ignore &#39;py&#39; (too small)",
                "Ignore &#39;xy&#39; (too small)",
                "Ignore &#39;z&#39; (too small)",
                "Error: no search term left, can&#39;t search",
                '<input type="text" name="search" value="py xy z" id="id_search" />',
                '<input type="submit" value="search" />',
                'Search Form',
            ),
            must_not_contain=(
                "Traceback", "Form errors", "field is required"
                'Search results',
                "Search in ", " plugins",
                "duration: ", "sec.",
                "hits: ",
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
        verbosity=1,
#        verbosity=0,
#        failfast=True
    )
