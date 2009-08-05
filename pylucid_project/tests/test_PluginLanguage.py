# coding:utf-8

import test_tools # before django imports!

#from django_tools.utils import info_print; info_print.redirect_stdout()

from django.conf import settings
from django.core.urlresolvers import reverse

from django_tools.unittest import unittest_base, BrowserDebug

from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests.test_tools.pylucid_test_data import TestSites, TestLanguages


URL_PREFIX = "/?language="


class LoginTest(basetest.BaseUnittest):
    ADMIN_INDEX_URL = reverse("admin:index")

    def setUp(self):
        """ I18N_DEBUG==True -> Display lang stuff in page_msg. """
        self.old_i18n_debug = settings.PYLUCID.I18N_DEBUG
        settings.PYLUCID.I18N_DEBUG = True

    def tearDown(self):
        settings.PYLUCID.I18N_DEBUG = self.old_i18n_debug

    def test_lang_switch(self):
        """
        The client requestes first a url with a lang code. This saves the language
        into the cookie "django_language".
        Every request after this, used the language from the cookie.
        """
        for lang in TestLanguages():
            for site in TestSites():
                info_string = "(lang:%s, site:%s)" % (lang.code, site.name)

                # remove previous cookies and session object, if exist.
                self.client.logout()

                # Test lang root page

                response = self.client.get("/%s/" % lang.code)
                must_contain = [
                    "1-rootpage content " + info_string,
                    "1-rootpage title " + info_string,

                    "Activate language &quot;%s&quot;" % lang.code,
                ]
                if lang.code == "en":
                    must_contain += ["Log in"]
                elif lang.code == "de":
                    must_contain += ["Anmelden"]
                else:
                    raise self.fail("Wrong language!")

                must_contain1 = must_contain[:]
                must_contain1 += ["Save lang code &quot;%s&quot;" % lang.code]
                self.assertResponse(response, must_contain1,
                    must_not_contain=('Error', "traceback", 'Permission denied'),
                )

                # Test if the language is ok, if no lang code is in url
                response = self.client.get("/")
                self.assertResponse(response, must_contain,
                    must_not_contain=(
                        'Error', "traceback", 'Permission denied',
                        "Save lang code"
                    ),
                )


                # Test if django admin page is in the right lang

                self.login(usertype="superuser")
                response = self.client.get(self.ADMIN_INDEX_URL)

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



if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__) # run all test from this file

#    from django.core import management
#    management.call_command('test', "test_PluginEditPage.CreateNewContentTest")
