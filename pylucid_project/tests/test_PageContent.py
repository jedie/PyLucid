# coding:utf-8

import test_tools # before django imports!

from django.conf import settings
from django.test import TransactionTestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site

from django_tools.unittest.unittest_base import BaseTestCase, direct_run

from pylucid.models import PageTree



class PageContentTest(BaseTestCase, TransactionTestCase):
    def __init__(self, *args, **kwargs):
        super(PageContentTest, self).__init__(*args, **kwargs)
    
        # Get the default lang code from system preferences
        from pylucid.preference_forms import SystemPreferencesForm
        system_preferences = SystemPreferencesForm().get_preferences()
        self.default_lang_code = system_preferences["lang_code"]
    
    def failUnlessEN(self, response):
        """ Check if **/firstpage/** is EN """
        self.assertResponse(response,
            must_contain=(
                '<a href="/firstpage/">1. en page</a>',
                '<h1>1. en test page!</h1>',
                '<a href="/de/firstpage/" title="switch to de - description">de</a>',
                '<a href="/en/firstpage/" title="switch to en - description">en</a>',
            ),
            must_not_contain=("Traceback",)#"error"),
        )
        
    def failUnlessDE(self, response):
        """ Check if **/firstpage/** is DE """
        self.assertResponse(response,
            must_contain=(
                '<a href="/firstpage/">1. de Seite</a>',
                '<h1>1. de test Seite!</h1>',
                '<a href="/de/firstpage/" title="switch to de - description">de</a>',
                '<a href="/en/firstpage/" title="switch to en - description">en</a>',          
            ),
            must_not_contain=("Traceback",)#"error"),
        )
        
    def failUnlessDefaultLang(self, response):
        """ Check if **/firstpage/** is in default language """
        if self.default_lang_code == "en":
            self.failUnlessEN(response)
        elif self.default_lang_code == "de":            
            self.failUnlessDE(response)
        else:
            raise AssertionError("default language %r unknown in unittest?!?" % self.default_lang_code)

    def failUnlessDefaultLangRedirect(self, response):
        """ Check if response is a redirect to the **/firstpage/** is in default language """
        expected_url = "http://testserver/%s/firstpage/" % self.default_lang_code
        self.assertRedirects(response, expected_url)
        response = self.client.get(expected_url)
        self.failUnlessDefaultLang(response)
        
    #-------------------------------------------------------------------------
        
    def test_en_request(self):      
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="en")
        self.failUnlessEN(response)
        response = self.client.get("/en/firstpage/")
        self.failUnlessEN(response)

    def test_de_request(self):
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE = "de")
        self.failUnlessDE(response)
        response = self.client.get("/de/firstpage/")
        self.failUnlessDE(response)
        
    def test_not_avaiable(self):
        """
        If a requested language doesn't exist -> Use the default language
        set in the preferences.
        
        TODO: If we can easy change a preferences value, we should use it
        and test different language codes.
        See also:
        http://code.google.com/p/django-dbpreferences/issues/detail?id=1
        """        
        response = self.client.get("/",
            HTTP_ACCEPT_LANGUAGE = "it,it-CH;q=0.8,es;q=0.5,ja-JP;q=0.3"
        )
        self.failUnlessDefaultLang(response)

    def test_wrong_url_lang1(self):
        response = self.client.get("/it/")
        self.assertRedirects(response, expected_url="/")
        
    def test_wrong_url_lang2(self):
        response = self.client.get("/it/firstpage/")
        self.failUnlessDefaultLangRedirect(response)
        


if __name__ == "__main__":
    # Run this unitest directly
    direct_run(__file__)