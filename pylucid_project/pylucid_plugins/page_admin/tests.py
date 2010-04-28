#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os


if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import reverse

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageContent, PageTree


CREATE_CONTENT_PAGE_URL = "/pylucid_admin/plugins/page_admin/new_content_page/"
CREATE_PLUGIN_PAGE_URL = "/pylucid_admin/plugins/page_admin/new_plugin_page/"
EDIT_ALL_URL = "/pylucid_admin/plugins/page_admin/edit_page/%i/"

INLINE_EDIT_PAGE_URL = "/?page_admin=inline_edit"
INLINE_PREVIEW_URL = "/?page_admin=preview"

ADD_CONTENT_PERMISSIONS = (
    "pylucid.add_pagecontent", "pylucid.add_pagemeta", "pylucid.add_pagetree"
)
CHANGE_CONTENT_PERMISSIONS = (
    "pylucid.change_pagecontent", "pylucid.change_pagemeta", "pylucid.change_pagetree"
)

class PageAdminTestCase(basetest.BaseLanguageTestCase):
    """
    inherited from BaseUnittest:
        - assertPyLucidPermissionDenied()
        - initial data fixtures with default test users
        - self.login()
    
    inherited from BaseLanguageTest:
        - self.default_language - system default Language model instance (default: en instance)
        - self.other_lang_code - alternative language code than system default (default: 'de')
        - self.other_language - alternative Language mode instance (default: de instance)
        - assertContentLanguage() - Check if response is in right language
    """
    def get_page_content_post_data(self, **kwargs):
        data = {
            'save': 'save',
            'content': 'The **creole** //content//.',
            'design': 1,
            'en-robots': 'index,follow',
            'markup': PageContent.MARKUP_CREOLE,
            'position': 0,
            'showlinks': 'on',
            'slug': 'page_slug'
        }
        data.update(kwargs)
        return data

    def login_with_permissions(self, permissions):
        """ login as normal user with PageAdmin add permissions """
        user = self.login("normal")
        self.add_user_permissions(user, permissions=permissions)


class PageAdminAnonymousTest(PageAdminTestCase):
    def test_login_before_create_content_page(self):
        """ Anonymous user must login, to use the create view """
        response = self.client.get(CREATE_CONTENT_PAGE_URL)
        self.assertRedirect(response, status_code=302,
            url="http://testserver/?auth=login&next_url=%s" % CREATE_CONTENT_PAGE_URL
        )

    def test_login_before_create_plugin_page(self):
        """ Anonymous user must login, to use the create view """
        response = self.client.get(CREATE_PLUGIN_PAGE_URL)
        self.assertRedirect(response, status_code=302,
            url="http://testserver/?auth=login&next_url=%s" % CREATE_PLUGIN_PAGE_URL
        )

    def test_login_before_edit_all(self):
        """ Anonymous user must login, to use the edit all view """
        url = EDIT_ALL_URL % 1 # edit the page with ID==1
        response = self.client.get(url)
        self.assertRedirect(response, status_code=302,
            url="http://testserver/?auth=login&next_url=%s" % url
        )


class PageAdminTest(PageAdminTestCase):
    """
    Test with a user witch are logged in and has ADD_PERMISSION
    """
    def setUp(self):
        self.client = Client() # start a new session
#
    def test__normal_user_without_permissions(self):
        """ test with insufficient permissions: normal, non-stuff user """
        self.login("normal")
        response = self.client.get(CREATE_CONTENT_PAGE_URL)
        self.assertPyLucidPermissionDenied(response)

    def test_staff_user_without_permissions(self):
        """ test with insufficient permissions: staff user without any permissions """
        self.login("staff")
        response = self.client.get(CREATE_CONTENT_PAGE_URL)
        self.assertPyLucidPermissionDenied(response)

    def test_create_page_form(self):
        """
        get the create page, with normal user witch has the add permission
        """
        self.login_with_permissions(ADD_CONTENT_PERMISSIONS)
        response = self.client.get(CREATE_CONTENT_PAGE_URL)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - Create a new page</title>',
                'form action="%s"' % CREATE_CONTENT_PAGE_URL,
                'input type="submit" name="save" value="save"',
                'textarea id="id_content"',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_create_entry(self):
        self.login_with_permissions(ADD_CONTENT_PERMISSIONS)
        response = self.client.post(CREATE_CONTENT_PAGE_URL,
            data=self.get_page_content_post_data()
        )
        new_page_url = "http://testserver/en/page_slug/"
        self.assertRedirect(response, url=new_page_url, status_code=302)

        # Check the created page
        response = self.client.get(new_page_url)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid CMS - page_slug</title>',
                'New content page u&#39;/en/page_slug/&#39; created.',
                '<p>The <strong>creole</strong> <i>content</i>.</p>',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_markup_preview(self):
        self.login_with_permissions(ADD_CONTENT_PERMISSIONS)
        response = self.client.post(CREATE_CONTENT_PAGE_URL,
            data=self.get_page_content_post_data(preview="markup preview")
            )
        self.assertResponse(response,
            must_contain=(
                '<p>The <strong>creole</strong> <i>content</i>.</p>',
                'The **creole** //content//.',
                '<title>PyLucid - Create a new page</title>',
                'form action="%s"' % CREATE_CONTENT_PAGE_URL,
                'input type="submit" name="save" value="save"',
                'textarea id="id_content"',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required")
        )

    def test_no_self_parent_choose(self):
        """
        Check if parent select doesn't conain the own entry.
        So the user can't select it and make a child <-> parent loop.
        """
        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)
        url = EDIT_ALL_URL % 1 # edit the page with ID==1
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<select name="parent" id="id_parent">',
                '<option value="" selected="selected">---------</option>',
                '<option value="3">/designs/</option>',
            ),
            must_not_contain=("Traceback", "Form errors", "field is required"
                '<option value="1">/welcome/</option>'
            )
        )

    def test_child_parent_loop_error(self):
        """
        do a child <-> parent loop: parent ID == current PageTree ID
        """
        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)
        url = EDIT_ALL_URL % 1 # edit the page with ID==1
        response = self.client.post(url,
            data=self.get_page_content_post_data(parent=1)
        )
        self.assertResponse(response,
            must_contain=(
                "Form errors",
                """<ul class="errorlist" id="parent_errors" title="Errors for field 'parent'">""",
                '<li>child-parent loop error!</li>',
            ),
            must_not_contain=("Traceback", "field is required")
        )

    def test_slug_exists_error(self):
        """
        use a slug that exist in the same sub tree.
        """
        # get two 'root' pages.
        first_test_page, second_test_page = PageTree.on_site.all().filter(parent=None)[:2]

        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)
        url = EDIT_ALL_URL % first_test_page.id # edit the first test page
        response = self.client.post(url,
            data=self.get_page_content_post_data(slug=second_test_page.slug)
        )
        self.assertResponse(response,
            must_contain=(
                "Form errors",
                """<ul class="errorlist" id="slug_errors" title="Errors for field 'slug'">""",
                "<li>Page '/<strong>%s</strong>/' exists already.</li>" % second_test_page.slug,
            ),
            must_not_contain=("Traceback", "field is required")
        )

    def test_plugin_page_parent_error(self):
        """
        A PageContent can't have a PluginPage as parent page.
        """
        # get any PluginPage
        a_plugin_page_id = PageTree.on_site.all().filter(page_type=PageTree.PLUGIN_TYPE)[0].id

        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)
        url = EDIT_ALL_URL % 1 # edit the page with ID==1
        response = self.client.post(url,
            data=self.get_page_content_post_data(parent=a_plugin_page_id)
        )
        self.assertResponse(response,
            must_contain=(
                "Form errors",
                """<ul class="errorlist" id="parent_errors" title="Errors for field 'parent'">""",
                "<li>Can't use the <strong>plugin</strong> page '/blog/' as parent page! Please choose a <strong>content</strong> page.</li>",
            ),
            must_not_contain=("Traceback", "field is required")
        )

class PageAdminInlineEditTest(PageAdminTestCase):
    """
    Test with a user witch are logged in and has ADD_PERMISSION
    """
    def setUp(self):
        self.client = Client() # start a new session

    def test_ajax_form(self):
        """ Test AJAX request of the edit page form """
        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)

        response = self.client.get(INLINE_EDIT_PAGE_URL, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                "Edit the CMS page '<strong>Welcome to your PyLucid CMS =;-)</strong>'",
                '&#x7B;% lucidTag update_journal %&#x7D;</textarea>', # PageContent
                # CSS:
                '#ajax_preview {',
                # JavaScript:
                '$("#ajax_preview").show();',
                # Some form strings:
                'input type="submit" name="save" value="save"',
                'form action="/?page_admin=inline_edit"',
                'textarea id="id_content"',
            ),
            must_not_contain=(
                '<title>', "<body", "<head>", # <- not a complete page
                "Traceback", 'Permission denied',
            ),
        )

    def test_ajax_preview(self):
        """ Test ajax edit page preview """
        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)

        response = self.client.post(INLINE_PREVIEW_URL,
            {"content": "A **creole** //preview//!", "preview": True},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.content,
            '<p>A <strong>creole</strong> <i>preview</i>!</p>\n'
        )


class ConvertMarkupTest(basetest.BaseLanguageTestCase):

    def _pre_setup(self, *args, **kwargs):
        """ create some language related attributes """
        super(ConvertMarkupTest, self)._pre_setup(*args, **kwargs)

        self.pagecontent = PageContent.objects.all().filter(markup=PageContent.MARKUP_TINYTEXTILE)[0]
        self.pagetree = PageTree.on_site.get(pagemeta=self.pagecontent.pagemeta)
        self.url = reverse("PageAdmin-convert_markup", kwargs={"pagecontent_id":self.pagecontent.id})

        self.login("superuser")

    def test_get_convert_form(self):
        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=(
                "<title>PyLucid - Convert &#39;tinyTextile&#39; markup</title>",
                'The original markup is: <strong>tinytextile</strong>',
                'h1. headlines',
            ),
            must_not_contain=(
                "Traceback", 'Permission denied',
            ),
        )

    def test_convert_verbose_preview(self):
        response = self.client.post(self.url, data={
            'content': '* 1.\n** 1.1.',
            'dest_markup': PageContent.MARKUP_CREOLE,
            'preview': 'Vorschau',
            'verbose': 'on'
        })
        self.assertResponse(response,
            must_contain=(
                "<title>PyLucid - Convert &#39;tinyTextile&#39; markup</title>",
                '<link rel="stylesheet" type="text/css" href="/headfile/pygments.css"',
                'The original markup is: <strong>tinytextile</strong>',
                '<legend class="pygments_code">Diff</legend>',
                '<span class="gd">- &lt;li&gt;1.&lt;/li&gt;</span>',
                '<span class="gi">+ &lt;li&gt;1.</span>',
                '<legend>new markup</legend>',
                '<pre>* 1.', '** 1.1.</pre>',
                'name="content">* 1.\n** 1.1.</textarea>'
            ),
            must_not_contain=(
                "Traceback", 'Permission denied',
            ),
        )

    def test_convert(self):
        response = self.client.post(self.url, data={
            'content': '* 1.\n** 1.1.',
            'dest_markup': PageContent.MARKUP_CREOLE,
        })
        new_url = "http://testserver%s" % self.pagecontent.get_absolute_url()
        self.assertRedirect(response,
            url=new_url,
            status_code=302
        )
        response = self.client.get(new_url)
        self.assertResponse(response,
            must_contain=(
                '<li>1.',
                '<li>1.1.</li>',
            ),
            must_not_contain=(
                "Traceback", 'Permission denied',
            ),
        )





if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', "pylucid_plugins.page_admin.tests.ConvertMarkupTest",
#        verbosity=0,
        verbosity=1,
        failfast=True
    )
#    management.call_command('test', __file__,
#        verbosity=1,
##        verbosity=0,
##        failfast=True
#    )
