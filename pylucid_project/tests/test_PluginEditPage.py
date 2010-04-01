# coding:utf-8

import os
import posixpath

import test_tools # before django imports!

#from django_tools.utils import info_print; info_print.redirect_stdout()

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django_tools.unittest_utils import unittest_base, BrowserDebug

from pylucid_project.apps.pylucid.models import EditableHtmlHeadFile, PageMeta, PageContent
from pylucid_project.apps.pylucid.preference_forms import SystemPreferencesForm

from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests import unittest_plugin


EDIT_PAGE_URL = "/?page_admin=inline_edit"
PREVIEW_URL = "/?page_admin=preview"
LOGIN_URL_PREFIX = "http://testserver/?auth=login"
LOGIN_URL = LOGIN_URL_PREFIX + "&next_url=/"
FORM_URL_PREFIX = "/pylucid_admin/plugins/page_admin"


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

    def test_new_plugin_permissions(self):
        """ anonymous user should be redirectet to the login page with a next_url. """
        response = self.client.get(self.new_plugin_url)
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(response['Location'],
            "http://testserver/?auth=login&next_url=/pylucid_admin/plugins/page_admin/new_plugin_page/"
        )

    def test_new_content_permissions(self):
        """ anonymous user should be redirectet to the login page with a next_url. """
        response = self.client.get(self.new_content_url)
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(response['Location'],
            "http://testserver/?auth=login&next_url=/pylucid_admin/plugins/page_admin/new_content_page/"
        )

    def test_new_content_form(self):
        """ Test if we get the "new content" input form """
        self.login(usertype="superuser")
        response = self.client.get(self.new_content_url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                "Create a new page",
                'form action="%s/new_content_page/" method="post" id="edit_page_form"' % FORM_URL_PREFIX,
                'input type="submit" name="save" value="save"',
                'textarea id="id_content"',
            ),
            must_not_contain=(
                "Traceback", 'Permission denied',
            ),
        )

# TODO:
#    def test_new_plugin_form(self):
#        """ Test if we get the "new plugin" input form """
#        self.login(usertype="superuser")
#        response = self.client.get(self.new_plugin_url)
#        self.failUnlessEqual(response.status_code, 200)
#        self.assertResponse(response,
#            must_contain=(
#                "Create a new plugin page",
#                'form action="%s/new_plugin_page/" method="post"' % FORM_URL_PREFIX,
#                'input type="submit" name="save" value="save"',
#                'select name="app_label" id="id_app_label"',
#                'option value="pylucid_project.pylucid_plugins.unittest_plugin"',
#            ),
#            must_not_contain=(
#                "Traceback", 'Permission denied',
#            ),
#        )

    def _test_create_page(self, form_url, page_type, extra_post_data, extra_must_contain):
        """
        Create a new page via POST.
        And check the created page via GET.
        """
        lang_code = self.default_lang_entry.code
        lang_desc = self.default_lang_entry.description
        for site in TestSites():
            info_string = "(lang: %s, site: %s)" % (lang_code, site.name)
            user = self.login(usertype="superuser")

            # Get the empty form
            response = self.client.get(form_url, HTTP_ACCEPT_LANGUAGE=lang_code)
            self.assertResponse(response,
                must_contain=(
                    "Create a new page",
                    "This new %s page will be create on site: '<strong>%s</strong>'" % (
                        page_type, site.domain
                    ),
                    "<legend>Language: <strong>%s</strong></legend>" % lang_desc,
                ),
                must_not_contain=('This field is required', "traceback")
            )

            post_data = {
                "position": "0",
                "design": "1",
                "slug": "new_%s_page_%s_%s" % (page_type, lang_code, site.name.replace(".", "_")),
                "name": "New %s page name %s" % (page_type, info_string),
                "title": "New %s page title %s" % (page_type, info_string),
                "robots": "follow and index me!",
                "keywords": "some, keywords, here ?",
                "description": "The %s page description. %s" % (page_type, info_string),
                "showlinks": "on",
            }
            for key, value in extra_post_data.items():
                post_data[key] = value % {"info_string": info_string}

            response = self.client.post(form_url, post_data, HTTP_ACCEPT_LANGUAGE=lang_code)
            self.assertResponse(response,
                must_not_contain=('This field is required', "error", "traceback")
            )
            #BrowserDebug.debug_response(response)

            new_page_url = "http://testserver/%s/%s/" % (lang_code, post_data["slug"])
            # Don't use self.assertRedirects here, because we can check the page_msg.
            self.failUnlessEqual(response.status_code, 302)
            self.failUnlessEqual(response['Location'], str(new_page_url)) # no unicode in headers

            # Check the new page
            response = self.client.get(new_page_url, HTTP_ACCEPT_LANGUAGE=lang_code)

            must_contain = [
                "New %s page" % page_type, "created.",
                post_data["name"],
                post_data["slug"],
                'meta name="robots" content="%s"' % post_data["robots"],
                'meta name="keywords" content="%s"' % post_data["keywords"],
                'meta name="description" content="%s"' % post_data["description"],
                '<title>%s' % post_data["title"],
                '<a href="/%s/%s/">%s</a>' % (lang_code, post_data["slug"], post_data["title"])
            ]
            for extra in extra_must_contain:
                must_contain.append(extra % {"info_string": info_string})

            self.assertResponse(response, must_contain,
                must_not_contain=(
                    "Traceback", 'Permission denied', 'This field is required',
                ),
            )

    def test_create_new_content_page(self):
        """ Create a new content page via POST and check the created page. """
        extra_post_data = {
            "content": "New page content %(info_string)s",
            "markup": "0",
        }
        extra_must_contain = [
            extra_post_data["content"]
        ]
        self._test_create_page(self.new_content_url, "content", extra_post_data, extra_must_contain)


#    def test_create_new_plugin_page(self):
#        """
#        Create a new plugin page via POST and check the created page.
#        Use the unittest_plugin.views.view_root() for this.
#        """
#        extra_post_data = {
#            "app_label": "pylucid_project.pylucid_plugins.unittest_plugin",
#            "urls_filename": "urls.py",
#        }
#        extra_must_contain = [
#            unittest_plugin.views.PLUGINPAGE_ROOT_STRING_RESPONSE
#        ]
#        self._test_create_page(self.new_plugin_url, "plugin", extra_post_data, extra_must_contain)


if __name__ == "__main__":
    # Run this unitest directly
#    from django_tools.utils import info_print; info_print.redirect_stdout()

#    unittest_base.direct_run(__file__) # run all test from this file

    from django.core import management
    management.call_command('test', "test_PluginEditPage.CreateNewContentTest")
