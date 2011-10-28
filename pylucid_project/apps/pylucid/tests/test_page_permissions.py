#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - related test in pylucid_plugins/language/tests.py
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.http import HttpRequest
from django.contrib.auth.models import Group

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import Language
from pylucid_project.apps.pylucid.models import PageTree


class TestPagePermissions(basetest.BaseUnittest):
    """
    inherited from BaseUnittest:
        - initial data fixtures with default test users
        - self.login()
    """
    def _pre_setup(self, *args, **kwargs):
        super(TestPagePermissions, self)._pre_setup(*args, **kwargs)

        self.test_group = Group(name="test group")
        self.test_group.save()

    def _set_pagetree_permitViewGroup(self, url):
        """ set self.test_group top the PageTree object get from url """
        user = self._get_user("superuser")
        request = HttpRequest() # Create a fake request
        request.user = user
        (page_tree, _, _) = PageTree.objects.get_page_from_url(request, url)
        page_tree.permitViewGroup = self.test_group
        page_tree.save()

    def assertCanSee(self, response):
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - The buildin creole markup.</title>',
            ),
            must_not_contain=("Traceback",)
        )
        self.assertStatusCode(response, 200)

    def test_no_permitViewGroup(self):
        """
        request a page, that is public
        """
        test_url = "example-pages/markups/creole"
        test_page_url = "/en/%s/" % test_url
        response = self.client.get(test_page_url)
        self.assertCanSee(response)

    def test_pagetree_permitViewGroup_1(self):
        """
        set a permitViewGroup on the last pagetree.
        """
        test_url = "example-pages/markups/creole"
        test_page_url = "/en/%s/" % test_url
        self._set_pagetree_permitViewGroup(test_url)
        response = self.client.get(test_page_url)
        self.assertPyLucidPermissionDenied(response)


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', __file__,
#        verbosity=1
        verbosity=0
    )
