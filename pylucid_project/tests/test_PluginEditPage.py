# coding:utf-8

import os
import posixpath

import test_tools # before django imports!

#from django_tools.utils import info_print
#info_print.redirect_stdout()

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django_tools.unittest import unittest_base, BrowserDebug

from pylucid.models import EditableHtmlHeadFile, PageMeta, PageContent
from pylucid_project.tests.test_tools import pylucid_test_data
from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests import unittest_plugin

EDIT_PAGE_URL = "/?page_admin=inline_edit"
PREVIEW_URL = "/?page_admin=preview"
LOGIN_URL = "http://testserver/?auth=login&next_url=/"

class EditPageInlineTest(basetest.BaseUnittest):
    """ Test for editing a page inline. """
    def assertCanNotEdit(self, response):
        #BrowserDebug.debug_response(response)
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
        """
        Test edit a page as a anonymous user
        The user should be redirected to a login page with next_url == EDIT_PAGE_URL
        """
        response = self.client.get(EDIT_PAGE_URL)
        self.assertRedirects(response, expected_url=LOGIN_URL, status_code=302)

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
                content_type = ContentType.objects.get_for_model(model)
                perm = Permission.objects.get(content_type=content_type, codename=permission)
                user.user_permissions.add(perm)

            user = self.login(usertype="normal") # "reloading" user to purge user._perm_cache 

            # low level check permissions:
            codenames = [u"pylucid.%s" % permission for permission, model in permissions]
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


class CreateNewContentTest(basetest.BaseUnittest):
    """ Test for creating new content/plugin page """

    def __init__(self, *args, **kwargs):
        super(CreateNewContentTest, self).__init__(*args, **kwargs)

        self.new_content_url = reverse("PageAdmin-new_content_page")
        self.new_plugin_url = reverse("PageAdmin-new_plugin_page")

    def test_permissions(self):
        """ anonymous user should be redirectet to the login page with a next_url. """
        for url in (self.new_content_url, self.new_plugin_url):
            response = self.client.get(url)
            self.assertRedirects(response,
                expected_url="http://testserver/?auth=login&next_url=" + url,
                status_code=302
            )

    def test_new_content_form(self):
        """ Test if we get the "new content" input form """
        self.login(usertype="superuser")
        response = self.client.get(self.new_content_url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                "Create a new page", "Create a new content page",
                'form action="/pylucid_admin/pylucid/new_content_page/" method="post" id="edit_page_form"',
                'input type="submit" name="save" value="save"',
                'textarea id="id_content"',
            ),
            must_not_contain=(
                "Traceback", 'Permission denied',
            ),
        )

    def test_new_plugin_form(self):
        """ Test if we get the "new plugin" input form """
        self.login(usertype="superuser")
        response = self.client.get(self.new_plugin_url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                "Create a new plugin page",
                'form action="/pylucid_admin/pylucid/new_plugin_page/" method="post"',
                'input type="submit" name="save" value="save"',
                'select name="app_label" id="id_app_label"',
                'option value="pylucid_project.pylucid_plugins.unittest_plugin"',
            ),
            must_not_contain=(
                "Traceback", 'Permission denied',
            ),
        )

    def test_create_new_content_page(self):
        """ Create a new content page via POST and check the created page. """
        self.login(usertype="superuser")
        post_data = {
            "position": "0",
            "design": "1",
            "slug": "new_content_page",
            "name": "The page name",
            "title": "A long page title",
            "lang": "1", # en
            "robots": "follow and index me!",
            "keywords": "some, keywords, here ?",
            "description": "a nice page description should be inserted here...",
            "content": "The new content page content ;)",
            "markup": "0",

        }
        response = self.client.post(self.new_content_url, post_data)
        #BrowserDebug.debug_response(response)
        new_page_url = "http://testserver/en/%s/" % post_data["slug"]
        self.assertRedirects(response, expected_url=new_page_url, status_code=302)

        # Check the new page
        response = self.client.get(new_page_url)
        self.assertResponse(response,
            must_contain=(
                post_data["content"],
                post_data["slug"],
                'meta name="robots" content="%s"' % post_data["robots"],
                'meta name="keywords" content="%s"' % post_data["keywords"],
                'meta name="description" content="%s"' % post_data["description"],
                '<title>%s' % post_data["title"],
                '<a href="/en/%s/">%s</a>' % (post_data["slug"], post_data["title"])
            ),
            must_not_contain=(
                "Traceback", 'Permission denied',
                'This field is required',
            ),
        )

    def test_create_new_plugin_page(self):
        """
        Create a new plugin page via POST and check the created page.
        Use the unittest_plugin.views.view_root() for this.
        """
        self.login(usertype="superuser")
        post_data = {
            "position": "0",
            "design": "1",
            "slug": "new_plugin_page",
            "name": "The page name",
            "title": "A long page title",
            "lang": "1", # en
            "robots": "follow and index me!",
            "keywords": "some, keywords, here ?",
            "description": "a nice page description should be inserted here...",
            "app_label": "pylucid_project.pylucid_plugins.unittest_plugin",
            "urls_filename": "urls.py",
        }
        response = self.client.post(self.new_plugin_url, post_data)
        #BrowserDebug.debug_response(response)
        new_page_url = "http://testserver/en/%s/" % post_data["slug"]
        self.assertRedirects(response, expected_url=new_page_url, status_code=302)

        # Check the new page
        response = self.client.get(new_page_url)
        self.assertResponse(response,
            must_contain=(
                unittest_plugin.views.PLUGINPAGE_ROOT_STRING_RESPONSE,
                post_data["slug"],
                'meta name="robots" content="%s"' % post_data["robots"],
                'meta name="keywords" content="%s"' % post_data["keywords"],
                'meta name="description" content="%s"' % post_data["description"],
                '<title>%s' % post_data["title"],
                '<a href="/en/%s/">%s</a>' % (post_data["slug"], post_data["title"])
            ),
            must_not_contain=(
                "Traceback", 'Permission denied',
                'This field is required',
            ),
        )


if __name__ == "__main__":
    # Run this unitest directly
#    from django_tools.utils import info_print; info_print.redirect_stdout()
    unittest_base.direct_run(__file__)
