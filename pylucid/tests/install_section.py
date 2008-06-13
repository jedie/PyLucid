#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test for the PyLucidCommonMiddleware

    FIXME: To test the PyLucid common middleware we need a way to test
    without the database tables.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import tests

from django.conf import settings

from PyLucid.models import Page

# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True


if settings.ENABLE_INSTALL_SECTION != True:
    print
    print "Info: Install section is disabled, some test will be skip!"


class TestBase(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    fixtures = [] # Run all test with a empty database

    install_url_base ="/%s" % settings.INSTALL_URL_PREFIX


class TestNoPage(TestBase):
    """
    Test the PyLucid behavior, if there exist no cms page. We should response
    the install help page.
    """

    def _assertHelpPageResponse(self, url):
        """
        Test if the given response is the help page.
        """
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                "Error getting a cms page",
                "solutions", "Please read the install guide",
            ),
        )
        return response

    def test_no_page(self):
        """
        Check if there is no page.
        """
        self.failUnlessEqual(Page.objects.all().count(), 0)

    def test_page_request(self):
        """
        Try to request a cms page, but there exist no tables, so we should
        get the help page response.
        """
        self._assertHelpPageResponse(url = "/")

    def test_page_permalink(self):
        """
        try to get the help page with a permalink.
        """
        url = "/%s/1/test" % settings.PERMALINK_URL_PREFIX
        self._assertHelpPageResponse(url)

    def test_command_url(self):
        """
        try to get the help page with a permalink.
        """
        url = "/%s/1/test/test/" % settings.COMMAND_URL_PREFIX
        self._assertHelpPageResponse(url)


class TestInstallSection(TestBase):
    """
    Test the _install section.
    """
    def setUp(self):
        settings.INSTALL_PASSWORD_HASH = (
            "sha1$000012345$1234567890abcdef00001234567890abcdef"
        )

    def _login(self):
        """
        Login into the _install section for later tests

        The test client is stateful. If a response returns a cookie, then that
        cookie will be stored in the test client and sent with all subsequent
        get() and post() requests, see:
        http://www.djangoproject.com/documentation/testing/#persistent-state
        """
        response = self.client.post(
            self.install_url_base, {"hash": settings.INSTALL_PASSWORD_HASH}
        )
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(settings.INSTALL_COOKIE_NAME in response.cookies)

        return response

    def test_login_page(self):
        """
        Request the install section login and check the reponse. Without any
        database table, we should be see the install secion login page.
        """
        if settings.ENABLE_INSTALL_SECTION != True:
            return

        response = self.client.get(self.install_url_base)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("Login into the _install section",),
            must_not_contain=("solutions", "Please read the install guide",),
        )

    def test_loginPOST(self):
        """
        Check if self._login() works
        """
        if settings.ENABLE_INSTALL_SECTION != True:
            return

        response = self._login()
        self.assertResponse(
            response,
            must_contain=("menu", "install", "syncdb", "update",),
            must_not_contain=("Login into the _install section",),
        )

    def test_access_deny(self):
        """
        Test if we get the login page, if a anonymous user will directly
        access a _install section view.
        """
        if settings.ENABLE_INSTALL_SECTION != True:
            return

        url = self.install_url_base + "/tests/info/"
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("Login into the _install section",),
            must_not_contain=("some information for developers:",),
        )

    def test_page_msg(self):
        """
        Test if the page_msg system works in the _install section.
        This tests depents on the page_msg output in the _install section
        view PyLucid.install.tests.info !
        """
        if settings.ENABLE_INSTALL_SECTION != True:
            return

        self._login()

        url = self.install_url_base + "/tests/info/"
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("some information for developers:",),
            must_not_contain=("Login into the _install section",),
        )



class TestMiddlewares(TestBase):
    """
    Test the PyLucid common middleware.
    If there exist not tables (e.g. starting installation) and the user request
    a cms page and not the _install section, he should get the install help
    page with some informations.

    TODO: Should we find a faster was to run the test without existing database
    tables?
    See: http://pylucid.org/phpBB2/viewtopic.php?p=1138#1138

    If we delete or rename the tables, we get this error:
        Error: Database :memory: couldn't be flushed.
    This messages comes from ./django/core/management/commands/flush.py
    """
    fixtures = [] # Run all test with a empty database

    def _drop_all_tables(self):
#        print "drop all tables...",
        from django.db import connection
        from django.core.management.sql import table_names

        cursor = connection.cursor()
        for table_name in table_names():
            statement = u"DROP TABLE %s;" % table_name
            cursor.execute(statement)
#        print "done"

    def _syncdb(self):
#        print "syncdb...",
        from django.core.management import call_command
        call_command('syncdb', verbosity=0, interactive=False)
#        print "done."

    def setUp(self):
        self._drop_all_tables()
#
    def tearDown(self):
        self._syncdb()

    def test(self):
        """
        Test if the given response is the help page.
        """
        response = self.client.get("/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                "Can&#39;t get a database table.",
                "solutions", "Please read the install guide",
            ),
            must_not_contain=("Error getting a cms page",)
        )

    def test_install_section(self):
        """
        Request the install section login. Without any database table, we
        should be see the install secion login page.
        """
#        self.assertInstallSectionLogin()
        url = self.install_url_base
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("Login into the _install section",),
        )


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])