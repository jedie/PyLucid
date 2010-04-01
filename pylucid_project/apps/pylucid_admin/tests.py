#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.core.urlresolvers import reverse
from django.test.client import Client

from pylucid_project.tests.test_tools import basetest



class AdminTest(basetest.BaseLanguageTestCase):
    ADMIN_INDEX_URL = reverse("admin:index")

    def setUp(self):
        self.client = Client() # start a new session

    def assertAdminLoginPage(self, response):
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                # django
                'form action="/admin/" method="post"',
                # from pylucid:
                '$("form").submit',
                '$("form").find(":submit")'
            ),
            must_not_contain=("Traceback",)
        )

    def test_admin_login(self):
        """ request the normal django admin login page """
        response = self.client.get(self.ADMIN_INDEX_URL)
        self.assertAdminLoginPage(response)

    def test_admin_index(self):
        self.login(usertype="superuser")
        response = self.client.get("/admin/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - Site administration</title>',
                '<a href="/pylucid_admin/install/pylucid/">install PyLucid</a>',
                '<a href="/pylucid_admin/install/plugins/">install plugins</a>',
            ),
            must_not_contain=("Traceback",
                # django
                'form action="/admin/" method="post"',
                # from pylucid:
                '$("form").submit',
                '$("form").find(":submit")'
            )
        )

    def test_install_plugins(self):
        self.login(usertype="superuser")
        response = self.client.get("/pylucid_admin/install/plugins/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - PyLucid - Plugin install</title>',
                '*** Install Plugins:',

                "PyLucidAdminPage &#39;new content page&#39;"
                " (&#39;/pylucid_admin/plugins/page_admin/new_content_page/&#39;)&gt; created.",
            ),
            must_not_contain=("Traceback",)
        )

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
        self.assertAdminLoginPage(response)

    def test_lang_german(self):
        """ Check if we get the admin page in the right language. """
        self.login(usertype="superuser")
        response = self.client.get(self.ADMIN_INDEX_URL, HTTP_ACCEPT_LANGUAGE="de")
        self.assertResponse(response,
            must_contain=(
                "PyLucid", "PageTree", "PageContent", "PageMeta",
                "Website-Verwaltung", "Kürzliche Aktionen"
            ),
            must_not_contain=("Log in", "Traceback",)
        )

if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=1)
