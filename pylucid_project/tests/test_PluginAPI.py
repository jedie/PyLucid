# coding: utf-8

"""
    PyLucid plugin API unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Test the plugin API with the unittest plugin. This plugin would be
    symlinked into "./pylucid_project/pylucid_plugins/" before the test
    starts. This would be done in pylucid_project.tests.test_tools.test_runner.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import test_tools # before django imports!

from django.conf import settings

from django_tools.unittest import unittest_base

from pylucid_project.tests.test_tools.pylucid_test_data import TestSites, TestLanguages
from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests import unittest_plugin

UNITTEST_GET_PREFIX = "?%s=" % unittest_plugin.views.GET_KEY
PLUGIN_PAGE_URL = "3-pluginpage" # Page created in pylucid_project.tests.test_tools.pylucid_test_data

class PluginGetViewTest(basetest.BaseUnittest):
    def test_get_view_none_response(self):
        """ http_get_view() returns None, the normal PageContent would be used. """
        url = UNITTEST_GET_PREFIX + unittest_plugin.views.ACTION_NONE_RESPONSE
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '1-rootpage content', # PageContent
                '<title>1-rootpage title',
            ),
            must_not_contain=(
                "Traceback",
                unittest_plugin.views.STRING_RESPONSE,
            ),
        )
        
    def test_get_view_string_response(self):
        """ http_get_view() returns a string, witch replace the PageContent. """
        url = UNITTEST_GET_PREFIX + unittest_plugin.views.ACTION_STRING_RESPONSE
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                unittest_plugin.views.STRING_RESPONSE,
                '<title>1-rootpage title',
            ),
            must_not_contain=(
                "Traceback",
                '1-rootpage content', # normal page content
            ),
        )
        
    def test_get_view_HttpResponse(self):
        """ http_get_view() returns a django.http.HttpResponse object. """
        url = UNITTEST_GET_PREFIX + unittest_plugin.views.ACTION_HTTP_RESPONSE
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.content, unittest_plugin.views.HTTP_RESPONSE)
        
    def test_get_view_Redirect(self):
        """ http_get_view() returns a django.http.HttpResponseRedirect object. """
        url = UNITTEST_GET_PREFIX + unittest_plugin.views.ACTION_REDIRECT
        response = self.client.get(url)
        self.assertRedirects(response, expected_url=unittest_plugin.views.REDIRECT_URL, status_code=302)


class PluginPageTest(basetest.BaseUnittest):
    def test_root_page(self):
        """
        Test the root view on all sites and in all test languages.
        """
        for site in TestSites():
            for language in TestLanguages():
                url = "/%s/%s/" % (language.code, PLUGIN_PAGE_URL)
                response = self.client.get(url)
                self.assertContentLanguage(response, language.code)
                self.assertResponse(response,
                    must_contain=(
                        unittest_plugin.views.PLUGINPAGE_ROOT_STRING_RESPONSE,
                        '3-pluginpage title (lang:%(lang)s, site:%(site_name)s) %(site_name)s' % {
                            "lang": language.code,
                            "site_name": site.name,
                        },
                    ),
                    must_not_contain=(
                        "Traceback",
                        '1-rootpage content', # normal page content
                    ),
                )
                
    def test_view_a(self):
        """
        Test a "url sub view" unittest_plugin.view_a().
        The view returns a HttpResponse object.
        """
        url = "/%s/%s/view_a/" % (self.default_lang_code, PLUGIN_PAGE_URL)
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.content, unittest_plugin.views.PLUGINPAGE_VIEW_A_STRING_RESPONSE)



if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)