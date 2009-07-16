# coding:utf-8

import test_tools # before django imports!

#from django_tools.utils import info_print
#info_print.redirect_stdout()

from django.conf import settings
from django.test import TransactionTestCase
from django.core.urlresolvers import reverse

from django_tools.unittest.unittest_base import BaseTestCase, direct_run


class PyLucidAdminMenu(BaseTestCase, TransactionTestCase):

    def setUp(self):
        """ install all existing plugins """
        self.login(usertype="superuser")
        response = self.client.get(reverse("PyLucidAdmin-install_plugins"))
        self.assertResponse(response,
            must_contain=("PyLucid - Plugin install", "install plugin", "page_admin"),
            must_not_contain=("Traceback",)
        )

    def test_superuser_admin_menu(self):
        """ get the admin menu as a superuser """
        self.login(usertype="superuser")
        response = self.client.get("/")
        self.assertResponse(response,
            must_contain=(
                "PyLucid", '<ul class="sf-menu">',
                reverse("PyLucidAdmin-menu"),
                reverse("PageAdmin-new_content_page"),
                reverse("PageAdmin-new_plugin_page"),
            ),
            must_not_contain=("Error", "Traceback",)
        )



if __name__ == "__main__":
    # Run this unitest directly
    direct_run(__file__)
