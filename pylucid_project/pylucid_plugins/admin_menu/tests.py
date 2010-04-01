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


from pylucid_project.tests.test_tools import basetest

class AdminMenuTest(basetest.BaseUnittest):
    def test_not_logged_in(self):
        """
        Admin menu must not in the page for anonymous users.
        """
        response = self.client.get("/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<a href="?auth=login"',
            ),
            must_not_contain=("Traceback",
                '<div class="PyLucidPlugins admin_menu" id="admin_menu_lucidTag">',
                '<a href="?auth=logout">Log out [superuser]</a>'
            )
        )

    def test_admin_menu(self):
        """
        Admin menu must be in the page, if the user is logged in.
        """
        self.login(usertype="superuser")
        response = self.client.get("/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<div class="PyLucidPlugins admin_menu" id="admin_menu_lucidTag">',
                '<a href="?auth=logout">Log out [superuser]</a>'
            ),
            must_not_contain=("Traceback",)
        )

if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=0)
