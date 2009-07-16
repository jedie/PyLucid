# coding:utf-8

import test_tools # before django imports!

#from django_tools.utils import info_print
#info_print.redirect_stdout()

from django.conf import settings
from django.test import TransactionTestCase
from django.core.urlresolvers import reverse

from django_tools.unittest.unittest_base import BaseTestCase, direct_run


class AdminSiteTest(BaseTestCase, TransactionTestCase):
    LOGIN_URL = "http://testserver/?auth=login&next_url=%s"

    def test_login_page(self):
        """ request the admin page index """
        url = reverse("admin_index")
        response = self.client.get(url)
        self.assertRedirects(response, status_code=302, expected_url=self.LOGIN_URL % url)

    def test_summary_page(self):
        self.login(usertype="superuser")
        response = self.client.get(reverse("admin_index"))
        self.assertResponse(response,
            must_contain=("PyLucid", "Page trees", "Page contents"),
            must_not_contain=("Log in", "Traceback",)#"error")
        )

    def test_anonymous_add(self):
        """ Try to create a PageTree entry as a anonymous user. """
        url = reverse("admin_pylucid_pagetree_add")
        response = self.client.get(url)
        self.assertRedirects(response, status_code=302, expected_url=self.LOGIN_URL % url)


if __name__ == "__main__":
    # Run this unitest directly
    direct_run(__file__)
