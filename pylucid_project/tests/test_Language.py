# coding:utf-8

import sys

import test_tools # before django imports!

#from django_tools.utils import info_print; info_print.redirect_stdout()

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from django_tools.unittest import unittest_base, BrowserDebug

from pylucid.models import Language

from pylucid_project.tests import unittest_plugin
from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests.test_tools.pylucid_test_data import TEST_LANGUAGES, TestLanguages


GET_VIEW_PREFIX = "?language="
RESET_GET_VIEW = GET_VIEW_PREFIX + "reset"


class BaseLangTest(basetest.BaseUnittest):
    def __init__(self, *args, **kwargs):
        super(BaseLangTest, self).__init__(*args, **kwargs)

        self.admin_index_url = reverse("admin:index")

    def setUp(self):
        """ I18N_DEBUG==True -> Display lang stuff in page_msg. """
        self.old_i18n_debug = settings.PYLUCID.I18N_DEBUG
        settings.PYLUCID.I18N_DEBUG = True

    def tearDown(self):
        settings.PYLUCID.I18N_DEBUG = self.old_i18n_debug

    def assertRenderedPage(self, response, slug, url, lang, site):
        sys.stdout.write(".")
        assert not url.startswith(lang.code)

        self.assertContentLanguage(response, lang)
        info_string = '(lang:' + lang.code + ', site:' + site.name + ')'

        data = {
            "slug": slug,
            "url": url,
            "lang_code": lang.code,
            "info_string": info_string,
        }

        must_contain = [
            # html meta tags (data from PageMeta):
            '<meta name="keywords" content="%(slug)s keywords %(info_string)s" />' % data,
            '<meta name="description" content="%(slug)s description %(info_string)s" />' % data,

            # Link from breadcrumbs plugin:
            '<a href="%(url)s" title="%(slug)s title %(info_string)s" class=' % data,

            # PageContent.content
            '%(slug)s content %(info_string)s' % data,
        ]
        must_not_contain = ["Traceback", ]

        deutsch_parts = [
            "Anmelden", # gettext from auth
            # Links from Language plugin:
            """<strong title="Current used language is 'deutsch'.">deutsch</strong>""",
            '<a href="?language=en" title="switch to english">',
        ]
        english_parts = [
            "Log in", # gettext from auth
            # Links from Language plugin:
            """<strong title="Current used language is 'english'.">english</strong>""",
            '<a href="?language=de" title="switch to deutsch">',
        ]

        if lang.code == "de":
            must_contain += deutsch_parts
            must_not_contain = english_parts
        elif lang.code == "en":
            must_contain += english_parts
            must_not_contain += deutsch_parts

        self.assertResponse(response, must_contain, must_not_contain)

    def assertRootPageLang(self, response, lang, site):
        """ Check if **/firstpage/** is in given language. """
        if lang.code == "en":
           self.assertRenderedPage(response, "1-rootpage", "/en/1-rootpage/", lang, site)
        elif lang.code == "de":
            self.assertRenderedPage(response, "1-rootpage", "/de/1-rootpage/", lang, site)
        else:
            raise self.fail("Wrong language!")

    def assertAdminLang(self, lang):
        """
        Test if django admin page is in the given language
        """
        self.login(usertype="superuser")
        response = self.client.get(self.admin_index_url)

        must_contain = ["PyLucid", "PageTree", "PageContent", "PageMeta"]
        if lang.code == "en":
            must_contain += ["Site administration", "Recent Actions"]
        elif  lang.code == "de":
            must_contain += ["Website-Verwaltung", "Kürzliche Aktionen"]
        else:
            raise

        self.assertResponse(response, must_contain,
            must_not_contain=("Log in", "Traceback",)#"error")
        )




class LanguagePluginTest(BaseLangTest):
    """ Test pylucid_plugins.Language """
    def test_get_views(self):
        """
        Test Language get views
        """
        site = Site.objects.get_current()
        for lang in TestLanguages():
            info_string = "(lang:%s, site:%s)" % (lang.code, site.name)

            # remove previous cookies and session object, if exist.
            self.client.logout()

            # No language is saved, we should get allways the client favored language
            response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=lang.code)
            self.assertRootPageLang(response, lang, site)

            # Save a language
            response = self.client.get("/" + GET_VIEW_PREFIX + lang.code)
            if response.status_code == 302:
                # Redirect to right language url
                url = response['Location']
                self.failUnlessEqual(url, "http://testserver/%s/1-rootpage/" % lang.code)
                response = self.client.get(url)

            # Check if response is in client favored language
            self.assertRootPageLang(response, lang, site)
            # Check if language was saved:
            self.assertResponse(response,
                must_contain=("Save lang code",), #<- page_msg in I18N_DEBUG mode
                must_not_contain=(
                    'Error', "traceback", 'Permission denied'
                ),
            )

            # The language was saved in the past. Check if we get the same language
            response = self.client.get("/")
            self.assertRootPageLang(response, lang, site)

            response = self.client.get("/%s/1-rootpage/" % lang.code)
            self.assertRootPageLang(response, lang, site)

            url = "/%s/2-rootpage/2-2-subpage/2-2-1-subpage/" % lang.code
            response = self.client.get(url)
            self.assertRenderedPage(response, "2-2-1-subpage", url, lang, site)

            # Test if django admin page is in client favored language
            self.assertAdminLang(lang)



class DetectLang(BaseLangTest):
    def test_wrong_url_lang1(self):
        """
        Test if we would be redirectet to the url with the right land code.
        Test view: pylucid.views.lang_root_page
        """
        for lang in TestLanguages():
            response = self.client.get("/it/", HTTP_ACCEPT_LANGUAGE=lang.code)
            self.failUnless(response['Location'], "/%s/" % lang.code)
            self.assertStatusCode(response, 302)

    def test_wrong_url_lang2(self):
        """
        Test if we would be redirectet to the url with the right land code.
        Test view: pylucid.views.resolve_url
        """
        for lang in TestLanguages():
            response = self.client.get("/it/1-rootpage/", HTTP_ACCEPT_LANGUAGE=lang.code)
            self.assertRedirect(response,
                url="http://testserver/%s/1-rootpage/" % lang.code, status_code=302
            )

    def test_redirect(self):
        """
        Test if we only redirected to existing entries.
        """
        # Create a language, but for this language exist no content.
        test_lang = Language(code="xx", description="has no content")
        test_lang.save()
        response = self.client.get("/1-rootpage/", HTTP_ACCEPT_LANGUAGE="xx")
        self.assertRedirect(response,
            url="http://testserver/%s/1-rootpage/" % self.default_lang_code, status_code=302
        )

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
            HTTP_ACCEPT_LANGUAGE="it,it-CH;q=0.8,es;q=0.5,ja-JP;q=0.3"
        )
        self.assertContentLanguage(response, self.default_lang_entry)
        self.assertResponse(response,
            must_contain=(
                "Favored language &quot;it&quot; does not exist",
                "Use default language &quot;%s&quot;" % self.default_lang_code,
                "Activate language &quot;%s&quot;" % self.default_lang_code,
            ),
            must_not_contain=("Traceback",)#"error"),
        )



if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__) # run all test from this file

#    from django.core import management
#    management.call_command('test', "test_Language.DetectLang")
