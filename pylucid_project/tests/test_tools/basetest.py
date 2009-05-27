#coding:utf-8

from django.test import TransactionTestCase
from django.contrib.sites.models import Site

from django_tools.unittest.unittest_base import BaseTestCase

class BaseUnittest(BaseTestCase, TransactionTestCase):
    def __init__(self, *args, **kwargs):
        super(BaseUnittest, self).__init__(*args, **kwargs)
    
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
        assert not url.startswith(lang_code)
        
        self.assertContentLanguage(response, lang_code)
        site = Site.objects.get_current()
        info_string = '(lang:'+lang_code+', site:'+site.name+')'
        
        data = {
            "slug": slug,
            "url": url, 
            "lang_code": lang_code,
            "info_string": info_string,
        }
        
        self.assertResponse(response,
            must_contain=(
                # html meta tags (data from PageMeta):
                '<meta name="keywords" content="%(slug)s keywords %(info_string)s" />' % data,
                '<meta name="description" content="%(slug)s description %(info_string)s" />' % data,
                
                # Link from breadcrumbs plugin:
                '<a href="/%(lang_code)s%(url)s">%(slug)s title %(info_string)s' % data,
                
                # PageContent.content
                '%(slug)s content %(info_string)s' % data,
                
                # Links from Language plugin:
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

