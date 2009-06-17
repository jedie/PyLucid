# coding:utf-8

import os
import posixpath

import test_tools # before django imports!

from django.conf import settings
from django.contrib.sites.models import Site

from django_tools.unittest import unittest_base

from pylucid_project.tests.test_tools import pylucid_test_data
from pylucid_project.tests.test_tools import basetest
from pylucid.models import EditableHtmlHeadFile


EDIT_PAGE_URL = "/?page_admin=inline_edit"

class EditPageTest(basetest.BaseUnittest):
    def assertCanNotEdit(self, response):
        self.failUnlessEqual(response.status_code, 403)
        self.assertResponse(response,
            must_contain=('Permission denied',),
            must_not_contain=(
                '1-rootpage content', # PageContent
                '<title>1-rootpage title',
            ),
        )
        
    def assertCanEdit(self, response):
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '1-rootpage content', # PageContent
                '<title>1-rootpage title',
            ),
            must_not_contain=(
                "Traceback", 'Permission denied',
            ),
        )
        
    def test_permissions_anonymous(self):
        """ Test edit a page as a anonymous user """
        response = self.client.get(EDIT_PAGE_URL)
        self.assertCanNotEdit(response)
        
    def test_permissions_superuser(self):
        """ Test edit a page as superuser """
        self.login(usertype="superuser")
        response = self.client.get(EDIT_PAGE_URL)
        self.assertCanEdit(response)
        
    def test_permissions_normal(self):
        """
        A normal user must have explicit permissions to edit a page.
        
        FIXME: Why can't i add permissions here??? They allways empty?!?!
        """
        user = self.login(usertype="normal")
        response = self.client.get(EDIT_PAGE_URL)
        self.assertCanNotEdit(response)
        
        # Give the test user the permissions:
        from django.contrib.auth.models import Permission
        for i in Permission.objects.all():
            print i.pk, i
        
        print user
        print user.get_all_permissions()
        print user._perm_cache
        user.user_permissions.add("pylucid.can_edit_pagecontent")
        user.user_permissions.add("pylucid.can_edit_pagemeta")
        user.save()
        user = self.login(usertype="normal")
        print user.get_all_permissions()
        print user._perm_cache
        
        self.failUnless(user.has_perms(["pylucid.can_edit_page", "pylucid.can_edit_pagemeta"]), "FIXME!!!")
        
        settings.DEBUG = True
        # Check if he can now edit the page:
        response = self.client.get(EDIT_PAGE_URL)
        self.assertCanEdit(response)



if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)