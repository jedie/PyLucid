# coding:utf-8

import test_tools # before django imports!

from django.conf import settings

from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site

from django_tools.unittest import unittest_base

from pylucid_project.tests.test_tools.pylucid_test_data import TestSites
from pylucid_project.tests.test_tools import basetest
from pylucid.models import PageTree

#settings.PYLUCID.I18N_DEBUG = True

class PageContentTest(basetest.BaseUnittest):
        
    def test_en_request(self):
        for site in TestSites():
            response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="en")
            self.failUnlessRootPageEN(response)
            
            response = self.client.get("/en/")
            self.failUnlessRootPageEN(response)
            
            response = self.client.get("/en/1-rootpage/")
            self.failUnlessRootPageEN(response)
            
            url = "/2-rootpage/2-2-subpage/2-2-1-subpage/"
            response = self.client.get("/en"+url)
            self.assertRenderedPage(response, "2-2-1-subpage", url, "en")

    def test_de_request(self):
        for site in TestSites():
            response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="de")
            self.failUnlessRootPageDE(response)
            
            response = self.client.get("/de/")
            self.failUnlessRootPageDE(response)
            
            response = self.client.get("/de/1-rootpage/")
            self.failUnlessRootPageDE(response)

            url = "/2-rootpage/2-2-subpage/2-2-1-subpage/"
            response = self.client.get("/de"+url)
            self.assertRenderedPage(response, "2-2-1-subpage", url, "de")

    def test_not_avaiable(self):
        """
        If a requested language doesn't exist -> Use the default language
        set in the preferences.
        
        TODO: If we can easy change a preferences value, we should use it
        and test different language codes.
        See also:
        http://code.google.com/p/django-dbpreferences/issues/detail?id=1
        """
        settings.PYLUCID.I18N_DEBUG = True
        
        response = self.client.get("/",
            HTTP_ACCEPT_LANGUAGE = "it,it-CH;q=0.8,es;q=0.5,ja-JP;q=0.3"
        )
        self.assertResponse(response,
            must_contain=(
                "Favored language &quot;it&quot; does not exist",
                "Use default language &quot;%s&quot;" % self.default_lang_code,
                "Activate language &quot;%s&quot;" % self.default_lang_code,   
            ),
            must_not_contain=("Traceback",)#"error"),
        )

    def test_wrong_url_lang1(self):
        response = self.client.get("/it/")
        self.assertRedirects(response, expected_url="/")
        
    def test_wrong_url_lang2(self):
        url = "/2-rootpage/2-1-subpage/"
        response = self.client.get("/it"+url)
        expected_url = "http://testserver/"+self.default_lang_code+url 
        self.assertRedirects(response, expected_url)
        response = self.client.get(expected_url)
        self.assertRenderedPage(response, "2-1-subpage", url, self.default_lang_code)
        

if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)