#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test PyLucid.plugins_internal.admin_menu

    TODO:

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

#______________________________________________________________________________
# Test:

import tests

from django.conf import settings

ONE_BROWSER_TRACEBACK = True

# Run test with:
PAGE_ID = 1

class TestPluginAdminMenu(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    def __init__(self, *args, **kwargs):
        super(TestPluginAdminMenu, self).__init__(*args, **kwargs)

        self.base_url = "/%s/%s/admin_menu/%%s/" % (
            settings.COMMAND_URL_PREFIX, PAGE_ID
        )
        self.sub_menu_url = self.base_url % "sub_menu"

    def test_rights(self):
        """
        get the admin sub menu as a anonymous user
        """
        response = self.client.get(self.sub_menu_url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("[Permission Denied!]",),
            must_not_contain=("Traceback", "Error",),
        )

    def test_sub_menu(self):
        """
        Check the sub menu
        Importand:
            Test works only, if unittest plugin was successfull installed!
        """
        self.login("superuser")

        response = self.client.get(self.sub_menu_url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(
                "Administration sub menu",
                "/_command/1/unittest_plugin/all_models/",
                "/_command/1/unittest_plugin/plugin_models/",
            ),
            must_not_contain=("[Permission Denied!]", "Traceback", "Error",),
        )




if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
