#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test for the PyLucidCommonMiddleware

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author: JensDiemer $

    :copyleft: 2008 by Jens Diemer.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os

import tests

from django.conf import settings

from django.db import connection, transaction
from django.db.models import get_app
from django.core.management import sql
from django.core.management.color import no_style


# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True


def drop_table():
    transaction.commit()
    cursor = connection.cursor()
    cursor.execute(u"DROP TABLE IF EXISTS django_session;")
    transaction.commit()


def drop_all_tables():
    """
    Delete all tables
    """
    app = get_app("PyLucid")
    statements = sql.sql_delete(app, no_style())
    cursor = connection.cursor()
    for statement in statements:
        cursor.execute(statement)


class TestBase(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

#    fixtures = []


class TestMiddlewares(TestBase):
#    def __init__(self, *arg, **kwargs):
#        drop_all_tables()
#        super(TestMiddlewares, self).__init__(*arg, **kwargs)

#    def setUp(self):
#        super(TestMiddlewares, self).setUp()
#        drop_all_tables()

    def test_page_request1(self):
        """
        Try to request a cms page, but there exist no tables, so we should
        get the help page response.
        """
#        drop_all_tables()
        response = self.client.get("/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("solutions", "Please read the install guide",),
        )

    def test_page_permalink(self):
        """
        try to get the help page with a permalink.
        """
#        drop_all_tables()
        response = self.client.get("/%s/1/test" % settings.PERMALINK_URL_PREFIX)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("solutions", "Please read the install guide",),
        )

    def test_install_section(self):
        """
        Request the install section login. Without any database table, we should
        be see the install secion login page.
        """
#        drop_all_tables()
        response = self.client.get("/" + settings.INSTALL_URL_PREFIX)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("Login into the _install section",),
            must_not_contain=("solutions", "Please read the install guide",),
        )



if __name__ == "__main__":
    # Run this unitest directly
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])