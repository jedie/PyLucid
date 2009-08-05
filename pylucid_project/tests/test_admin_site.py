# coding:utf-8

import test_tools # before django imports!

#from django_tools.utils import info_print
#info_print.redirect_stdout()

from django.conf import settings
from django.test import TransactionTestCase
from django.core.urlresolvers import reverse

from django_tools.unittest.unittest_base import BaseTestCase, direct_run

from pylucid_project.tests.test_tools.pylucid_test_data import TestLanguages


class AdminSiteTest(BaseTestCase, TransactionTestCase):
    LOGIN_URL = "http://testserver/?auth=login&next_url=%s"
    ADMIN_INDEX_URL = reverse("admin:index")

    def test_login_page(self):
        """ request the admin page index """
        response = self.client.get(self.ADMIN_INDEX_URL)
        self.assertRedirects(response, status_code=302, expected_url=self.LOGIN_URL % self.ADMIN_INDEX_URL)

    def test_summary_page(self):
        self.login(usertype="superuser")
        response = self.client.get(self.ADMIN_INDEX_URL)
        self.assertResponse(response,
            must_contain=("PyLucid", "PageTree", "PageContent", "PageMeta"),
            must_not_contain=("Log in", "Traceback",)#"error")
        )

    def test_anonymous_add(self):
        """ Try to create a PageTree entry as a anonymous user. """
        url = reverse("admin:pylucid_pagetree_add")
        response = self.client.get(url)
        self.assertRedirects(response, status_code=302, expected_url=self.LOGIN_URL % url)

    def test_lang(self):
        """ Check if we get the admin page in the right language. """
        for lang in TestLanguages():
            self.login(usertype="superuser")
            response = self.client.get(self.ADMIN_INDEX_URL, HTTP_ACCEPT_LANGUAGE=lang.code)

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
    direct_run(__file__)
