#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the plugin manager permission system.

    This is not a test, if the plugin manager response the right error or
    exception! For this case .../tests/debug_mode.py is responsible.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import tests
from tests import TEST_USERS, TEST_UNUSABLE_USER

from django.conf import settings

from PyLucid.models import User

# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True


class TestBase(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    def setUp(self):
        settings.DEBUG=False

        self.base_url = "/%s/1" % settings.COMMAND_URL_PREFIX

    def _access_deny_test(self):
        plugin_name = "page_admin"
        method_names = (
            "edit_page", "new_page", "select_edit_page",
            "delete_pages", "sequencing"
        )
        self.assertAccessDenied(self.base_url, plugin_name, method_names)


class AnonymousTest(TestBase):
    """
    Try to access restricted _command methods as a anonymous user.
    """
    def test_access_deny(self):
        self._access_deny_test()


class DeactivatedUserTest(TestBase):
    """
    Try to access restricted _command methods as a not active user.
    """
    def test_access_deny(self):
        # Deactivate all users
        for user in User.objects.all():
            user.is_active = False

        self._access_deny_test()


class NotAdminTest(TestBase):
    """
    Tests with a login user
    """
    def setUp(self):
        super(NotAdminTest, self).setUp()
        self.login("normal")

    def test_access_allowed(self):
        plugin_name = "page_admin"
        method_names = (
            "edit_page", "new_page", "select_edit_page",
            "delete_pages", "sequencing"
        )
        self.assertAccessAllowed(self.base_url, plugin_name, method_names)



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename], verbosity=1)