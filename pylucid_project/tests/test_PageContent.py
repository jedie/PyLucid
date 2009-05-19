# coding:utf-8

import test_tools # before django imports!

from django.conf import settings
from django.test import TransactionTestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site

from django_tools.unittest.unittest_base import BaseTestCase, direct_run

from pylucid_project.tests.test_tools.pylucid_test_data import TestSites
from pylucid.models import PageTree

#settings.PYLUCID.I18N_DEBUG = True

class PageContentTest(BaseTestCase, TransactionTestCase):
    def __init__(self, *args, **kwargs):
        super(PageContentTest, self).__init__(*args, **kwargs)
    
        # Get the default lang code from system preferences
        from pylucid.preference_forms import SystemPreferencesForm
        system_preferences = SystemPreferencesForm().get_preferences()
        self.default_lang_code = system_preferences["lang_code"]
    
    def assertContentLanguage(self, response, lang_code):
        is_lang = response["content-language"]
        self.failUnlessEqual(is_lang, lang_code,
            "Header 'Content-Language' is not '%s' it's: '%s'" % (lang_code, is_lang)
        )
        self.assertResponse(response,
            must_contain=('<meta name="DC.Language" content="%s">' % lang_code,)
        )
    
    def assertRenderedPage(self, response, slug, url, lang_code):
        self.assertContentLanguage(response, lang_code)
        site = Site.objects.get_current()
        info_string = '(lang:'+lang_code+', site:'+site.name+')'
        
        data = {
            "slug": slug,
            "url": url, 
            "info_string": info_string,
        }
        
        self.assertResponse(response,
            must_contain=(
                #'<meta name="keywords" content="%(slug)s keywords %(info_string)s" />' % data,
                '<meta name="description" content="%(slug)s description %(info_string)s" />' % data,                
                '<a href="%(url)s">%(slug)s title %(info_string)s' % data,
                '%(slug)s content %(info_string)s' % data,
                '<a href="/de%(url)s" title="switch to deutsch">de</a>' % data,
                '<a href="/en%(url)s" title="switch to english">en</a>' % data,
            ),
            must_not_contain=("Traceback",)#"error"),
        )
    
    def failUnlessRootPageEN(self, response):
        """ Check if **/firstpage/** is EN """
        self.assertRenderedPage(response, "1-rootpage", "/1-rootpage/", "en")
        
    def failUnlessRootPageDE(self, response):
        """ Check if **/firstpage/** is DE """
        self.assertRenderedPage(response, "1-rootpage", "/1-rootpage/", "de")
        
    def failUnlessRootPageDEfaultLang(self, response):
        """ Check if **/firstpage/** is in default language """
        if self.default_lang_code == "en":
            self.failUnlessRootPageEN(response)
        elif self.default_lang_code == "de":            
            self.failUnlessRootPageDE(response)
        else:
            raise AssertionError("default language %r unknown in unittest?!?" % self.default_lang_code)

    def failUnlessRootPageDEfaultLangRedirect(self, response):
        """ Check if response is a redirect to the **/firstpage/** is in default language """
        expected_url = "http://testserver/%s/firstpage/" % self.default_lang_code
        self.assertRedirects(response, expected_url)
        response = self.client.get(expected_url)
        self.failUnlessRootPageDEfaultLang(response)
        
    #-------------------------------------------------------------------------
        
    def test_en_request(self):
        for site in TestSites():
            response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="en")
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
    direct_run(__file__)