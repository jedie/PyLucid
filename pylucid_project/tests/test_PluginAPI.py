# coding:utf-8

import test_tools # before django imports!

from django.conf import settings

from django_tools.unittest import unittest_base

from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests import unittest_plugin

UNITTEST_GET_PREFIX = "?%s=" % unittest_plugin.views.GET_KEY

class PluginApiTest(basetest.BaseUnittest):
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
        self.assertContains(response, text=unittest_plugin.views.HTTP_RESPONSE, count=1, status_code=200)
        
    def test_get_view_HttpResponse(self):
        """ http_get_view() returns a django.http.HttpResponseRedirect object. """
        url = UNITTEST_GET_PREFIX + unittest_plugin.views.ACTION_REDIRECT
        response = self.client.get(url)
        self.assertRedirects(response, expected_url=unittest_plugin.views.REDIRECT_URL, status_code=302)





if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)