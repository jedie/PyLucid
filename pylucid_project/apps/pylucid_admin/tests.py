#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test.client import Client

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid_admin.models import PyLucidAdminPage


class PyLucidAdminTestCase(basetest.BaseUnittest):
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


class PyLucidAdminTest(PyLucidAdminTestCase):

    def test_unique_url_name(self):
        """ Check if url_name must be unique. """
        test_url_name = "unittest"
        first_entry = PyLucidAdminPage(name="foo", url_name=test_url_name)
        first_entry.save()
        second_entry = PyLucidAdminPage(name="bar", url_name=test_url_name)
        self.failUnlessRaises(ValidationError, second_entry.full_clean)

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


class PyLucidPluginsTest(PyLucidAdminTestCase):
    """ Tests with installed plugins """
    def _pre_setup(self, *args, **kwargs):
        """ create some blog articles """
        super(PyLucidPluginsTest, self)._pre_setup(*args, **kwargs)

        # TODO: use managment command for this, if exist ;)
        self.login(usertype="superuser")
        response = self.client.get("/pylucid_admin/install/plugins/")
        self.failUnless(PyLucidAdminPage.objects.count() > 0, response.content + "\n\nno plugins installed?")

    def assertLoginRedirect(self, response, url):
        login_url = 'http://testserver/?auth=login&next_url=%s' % url
        self.assertRedirect(response, login_url, status_code=302)

    def assertIsAdminPage(self, url):
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - ',
                '<h1 class="admin_headline">PyLucid',
                '<meta name="robots" content="NONE,NOARCHIVE" />',
            ),
            must_not_contain=(
                "Permission denied",
                'input id="id_password"',
            )
        )
        self.failUnlessEqual(response.status_code, 200)

    def test_access_admin_views(self):
        """
        request all existing PyLucid admin views from every plugin.
        
        This test check a few things:
            - test the access security of pylucid admin views
            - check if admin url permissions are ok
        """
        all_plugin_views = PyLucidAdminPage.objects.exclude(url_name=None)
        for item in all_plugin_views:
            sys.stdout.write(".")

            url = item.get_absolute_url()
            superuser_only, access_permissions = item.get_permissions()
#            print item
#            print superuser_only
#            print access_permissions

            # anonymous user should never have access to any pylucid admin view
            self.client = Client() # start a new session
            response = self.client.get(url)
            self.assertLoginRedirect(response, url)

            # try with normal, non-staff user without any permissions
            self.client = Client() # start a new session
            self.login(usertype="normal")
            if not superuser_only and not access_permissions:
                # admin view needs not explicit permissions
                self.assertIsAdminPage(url)
                continue
            else:
                # it's not accessible by normal user
                self.assertLoginRedirect(response, url)

            # start a new session
            self.client = Client()
            self.login_with_permissions(usertype="normal", permissions=access_permissions)
            if not superuser_only:
                # user needs permissions and has it
                self.assertIsAdminPage(url)
                continue

            # only accessible for superusers -> try as staff user with permissions
            # start a new session
            self.client = Client()
            self.login_with_permissions(usertype="staff", permissions=access_permissions)
            self.assertLoginRedirect(response, url)

            # Access superuser only view as a superuser
            # start a new session
            self.client = Client()
            self.login(usertype="superuser")
            self.assertIsAdminPage(url)





if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', "apps.pylucid_admin.tests.PyLucidPluginsTest",
#        verbosity=0,
        verbosity=1,
        failfast=True
    )
#    management.call_command('test', __file__,
#        verbosity=1,
##        verbosity=0,
##        failfast=True
#    )
