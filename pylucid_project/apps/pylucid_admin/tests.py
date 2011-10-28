#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test.client import Client

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid_admin.models import PyLucidAdminPage


ADMIN_TEST_URL_NAME = "PageAdmin-new_content_page"


class PyLucidAdminTestCase(basetest.BaseUnittest):
    ADMIN_INDEX_URL = reverse("admin:index")

    def setUp(self):
        self.client = Client() # start a new session


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
        self.assertStatusCode(response, 200)
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
        self.assertStatusCode(response, 200)
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
        self.assertResponse(response,
            must_contain=("Install Plugins:", "install plugin"),
            must_not_contain=("Log in", "Traceback")
        )

    def assertLoginRedirect(self, url):
        login_url = 'http://testserver/?auth=login&next_url=%s' % url
        response = self.client.get(url)
        self.assertRedirect(response, login_url, status_code=302)

    def assertIsAdminPage(self, url):
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<html', '<head>', '<title>', '<body',
                '<meta name="robots" content="NONE,NOARCHIVE" />',
                '<ul class="sf-menu">', 'PyLucid admin menu',
            ),
            must_not_contain=(
                '<input type="text" name="username"',
                '<input type="password" name="password"',
                '<input type="submit" value="Log in" />',
            )
        )
        self.assertStatusCode(response, 200)

    def assertPermissionDenied(self, url):
        response = self.client.get(url)
        self.assertPyLucidPermissionDenied(response)

    def test_access_admin_views(self):
        """ Test different user permission access of pylucid admin views. """
        # Remember all test cases
        superuser_only_tested = False
        must_staff_only_tested = False
        permissions_only_tested = False

        all_plugin_views = PyLucidAdminPage.objects.exclude(url_name=None)
        for item in all_plugin_views:
            url = item.get_absolute_url()
            superuser_only, permissions, must_staff = item.get_permissions()

            if superuser_only:
                # Test admin view for superusers only
                if superuser_only_tested: # Test only one time
                    continue
                superuser_only_tested = True

                # Anonymous user should have no access:
                self.client = Client() # start a new session
                self.assertLoginRedirect(url)

                self.login(usertype="normal")
                self.assertPermissionDenied(url)

                self.login(usertype="staff")
                self.assertPermissionDenied(url)

                self.login(usertype="superuser")
                self.assertIsAdminPage(url)

            elif must_staff and not permissions:
                # User must be staff member, but must not have any permissions
                if must_staff_only_tested: # Test only one time
                    continue
                must_staff_only_tested = True

                self.client = Client() # start a new session
                self.assertLoginRedirect(url) # Anonymous user

                self.login(usertype="normal")
                self.assertPermissionDenied(url)

                self.login(usertype="staff")
                self.assertIsAdminPage(url)

            elif permissions and not must_staff:
                # Normal users with the right permissions can use this view
                if permissions_only_tested: # Test only one time
                    continue
                permissions_only_tested = True

                self.client = Client() # start a new session
                self.assertLoginRedirect(url) # Anonymous user

                # Normal user, without any permissions
                self.login(usertype="normal")
                self.assertPermissionDenied(url)

                # Normal user with the right permissions
                self.login_with_permissions(usertype="staff", permissions=permissions)
                self.assertIsAdminPage(url)

            sys.stdout.write(".")

        # Check if every case was tested
        self.failUnless(superuser_only_tested == True)
        self.failUnless(must_staff_only_tested == True)
        self.failUnless(permissions_only_tested == True)





if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    tests = __file__
#    tests = "apps.pylucid_admin.tests.PyLucidPluginsTest.test_access_admin_views"

    management.call_command('test', tests,
#        verbosity=0,
        verbosity=1,
        failfast=True
    )
