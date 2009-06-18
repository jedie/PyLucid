# coding:utf-8

import os
import posixpath

import test_tools # before django imports!

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django_tools.unittest import unittest_base

from pylucid_project.tests.test_tools import pylucid_test_data
from pylucid_project.tests.test_tools import basetest
from pylucid.models import EditableHtmlHeadFile, PageMeta, PageContent

EDIT_PAGE_URL = "/?page_admin=inline_edit"
PREVIEW_URL = "/?page_admin=preview"

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
        """ assert that the response is the edit page form """
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '1-rootpage content', # PageContent
                '<title>1-rootpage title',
                # Some form strings:
                'input type="submit" name="save" value="save"',
                'form action="/?page_admin=inline_edit"',
                'textarea id="id_content"',
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
        """ A normal user must have explicit permissions to edit a page. """
        
        def check_permissions(permissions, assertion):
            user = self.login(usertype="normal")
            user.user_permissions.clear() # Delete all existing permissions
            for permission, model in permissions:
                # Give the test user the permissions:
                content_type=ContentType.objects.get_for_model(model)
                perm = Permission.objects.get(content_type=content_type, codename=permission)
                user.user_permissions.add(perm)
            
            user = self.login(usertype="normal") # "reloading" user to purge user._perm_cache 
            
            # low level check permissions:
            codenames = [u"pylucid.%s" % permission for permission,model in permissions]
            self.failUnless(user.has_perms(codenames),
                "Low level error, user has not permissions: %r, he has: %r" % (
                    codenames, user.get_all_permissions()
                )
            )
            # Check if he can now edit the page:
            response = self.client.get(EDIT_PAGE_URL)
            assertion(response)
        
        # normal user has no permissions
        check_permissions(permissions=[], assertion=self.assertCanNotEdit)
        
        # normal user has only one permission
        check_permissions(
            permissions=[("change_pagecontent", PageContent)],
            assertion=self.assertCanNotEdit
        )
        check_permissions(
            permissions=[("change_pagemeta", PageMeta)],
            assertion=self.assertCanNotEdit
        )
        
        # normal user has all permission -> he can edit the page
        check_permissions(
            permissions=[("change_pagecontent", PageContent), ("change_pagemeta", PageMeta)],
            assertion=self.assertCanEdit
        )

    def test_ajax_form(self):
        """ Test AJAX request of the edit page form """
        self.login(usertype="superuser")
        response = self.client.get(EDIT_PAGE_URL, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '1-rootpage content', # PageContent
                # addition javascript from {% extrahead %} block:
                '<!-- extrahead from .../apps/pylucid/defaulttags/extraheadBlock.py', 
                # Some form strings:
                'input type="submit" name="save" value="save"',
                'form action="/?page_admin=inline_edit"',
                'textarea id="id_content"',
            ),
            must_not_contain=(
                '<title>1-rootpage title', "<body", "<head>", # <- not a complete page
                "Traceback", 'Permission denied',
            ),
        )
    
    def test_ajax_preview(self):
        """ Test ajax edit page preview """
        self.login(usertype="superuser")       
        response = self.client.post(PREVIEW_URL,
            {"content": "==headline"},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual("<h2>headline</h2>\n", response.content)



if __name__ == "__main__":
    # Run this unitest directly
#    from django_tools.utils import info_print; info_print.redirect_stdout()
    unittest_base.direct_run(__file__)