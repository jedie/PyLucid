#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
    
    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys

if __name__ == "__main__":
    # Run all unittest directly

    tests = __file__
#    tests = "pylucid_plugins.page_admin.tests.BulkEditorCsrfTest"
#    tests = "pylucid_plugins.page_admin.tests.PageAdminTest.test_translate_form"

    from pylucid_project.tests import run_test_directly
    run_test_directly(tests,
        verbosity=2,
#        failfast=True,
        failfast=False,
    )
    sys.exit()

from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import reverse

from pylucid_project.apps.pylucid.markup import MARKUP_CREOLE, \
    MARKUP_TINYTEXTILE
from pylucid_project.apps.pylucid.models import PageContent, PageTree
from pylucid_project.tests.test_tools import basetest


CREATE_CONTENT_PAGE_URL = reverse("PageAdmin-new_content_page")
CREATE_PLUGIN_PAGE_URL = reverse("PageAdmin-new_plugin_page")

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
            'markup': MARKUP_CREOLE,
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
        url = reverse("PageAdmin-edit_page", kwargs={"pagetree_id":1}) # edit the page with ID==1
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
        self.assertStatusCode(response, 200)

        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        csrf_token = csrf_cookie.value

        # XXX: work-a-round for: https://github.com/gregmuellegger/django/issues/1
        response.content = response.content.replace(
            """.before('<h2 class="ajax_msg">submit...</h2>');""",
            """.before('submit...');""",
        )
        response.content = response.content.replace(
            """.html('<h2 class="noanchor">loading...</h2>');""",
            """.html('loading...');"""
        )
        self.assertDOM(response,
            must_contain=(
                '<title>PyLucid - Create a new page</title>',
                "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % csrf_token,
                '<input type="submit" name="save" value="Save" />',
                '<textarea id="id_content" rows="10" cols="40" name="content"></textarea>',
                '<input type="button" id="preview_submit_id_content" name="preview" value="markup preview" />',
                '<legend>Markup preview</legend>',
            )
        )
        self.assertResponse(response,
            must_contain=(
                'form action="%s"' % CREATE_CONTENT_PAGE_URL,
            ),
            must_not_contain=("XXX INVALID TEMPLATE STRING", "Traceback", "Form errors", "field is required")
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
            must_not_contain=("XXX INVALID TEMPLATE STRING", "Traceback", "Form errors", "field is required")
        )

    def test_markup_preview(self):
        self.login_with_permissions(ADD_CONTENT_PERMISSIONS)
        response = self.client.post(
            CREATE_CONTENT_PAGE_URL + "preview/",
            data=self.get_page_content_post_data(preview="markup preview"),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertResponse(response,
            must_contain=(
                '<p>The <strong>creole</strong> <i>content</i>.</p>',
            ),
            must_not_contain=("XXX INVALID TEMPLATE STRING", "Traceback", "error", "field is required")
        )

    def test_no_self_parent_choose(self):
        """
        Check if parent select doesn't conain the own entry.
        So the user can't select it and make a child <-> parent loop.
        """
        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)
        url = reverse("PageAdmin-edit_page", kwargs={"pagetree_id":1}) # edit the page with ID==1
        response = self.client.get(url)

        # XXX: work-a-round for: https://github.com/gregmuellegger/django/issues/1
        response.content = response.content.replace(
            """.before('<h2 class="ajax_msg">submit...</h2>');""",
            """.before('submit...');""",
        )
        response.content = response.content.replace(
            """.html('<h2 class="noanchor">loading...</h2>');""",
            """.html('loading...');"""
        )

        self.assertDOM(response,
            must_contain=(
                '<option value="" selected="selected">---------</option>',
                '<option value="3">/designs/</option>',
            ),
            must_not_contain=(
                '<option value="1">/welcome/</option>',
            )
        )
        self.assertResponse(response,
            must_contain=(
                '<select', 'id="id_parent"', 'name="parent"',
            ),
            must_not_contain=("XXX INVALID TEMPLATE STRING",
                "Traceback", "Form errors", "field is required"
            )
        )

    def test_child_parent_loop_error(self):
        """
        do a child <-> parent loop: parent ID == current PageTree ID
        """
        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)
        url = reverse("PageAdmin-edit_page", kwargs={"pagetree_id":1}) # edit the page with ID==1
        response = self.client.post(url,
            data=self.get_page_content_post_data(parent=1)
        )
        self.assertResponse(response,
            must_contain=(
                "Form errors",
                """<ul class="errorlist" id="parent_errors" title="Errors for field 'parent'">""",
                '<li>child-parent loop error!</li>',
            ),
            must_not_contain=("XXX INVALID TEMPLATE STRING", "Traceback", "field is required")
        )

    def test_slug_exists_error(self):
        """
        use a slug that exist in the same sub tree.
        """
        # get two 'root' pages.
        first_test_page, second_test_page = PageTree.on_site.all().filter(parent=None)[:2]

        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)
        url = reverse("PageAdmin-edit_page", kwargs={"pagetree_id":first_test_page.id}) # edit the first test page
        response = self.client.post(url,
            data=self.get_page_content_post_data(slug=second_test_page.slug)
        )
        self.assertResponse(response,
            must_contain=(
                "Form errors",
                """<ul class="errorlist" id="slug_errors" title="Errors for field 'slug'">""",
                "<li>Page '/<strong>%s</strong>/' exists already.</li>" % second_test_page.slug,
            ),
            must_not_contain=("XXX INVALID TEMPLATE STRING", "Traceback", "field is required")
        )

    def test_plugin_page_parent_error(self):
        """
        A PageContent can't have a PluginPage as parent page.
        """
        # get any PluginPage
        a_plugin_page_id = PageTree.on_site.all().filter(page_type=PageTree.PLUGIN_TYPE)[0].id

        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)
        url = reverse("PageAdmin-edit_page", kwargs={"pagetree_id":1}) # edit the page with ID==1
        response = self.client.post(url,
            data=self.get_page_content_post_data(parent=a_plugin_page_id)
        )
        self.assertResponse(response,
            must_contain=(
                "Form errors",
                """<ul class="errorlist" id="parent_errors" title="Errors for field 'parent'">""",
                "<li>Can't use the <strong>plugin</strong> page '/blog/' as parent page! Please choose a <strong>content</strong> page.</li>",
            ),
            must_not_contain=("XXX INVALID TEMPLATE STRING", "Traceback", "field is required")
        )

    def test_tag_list(self):
        self.login_with_permissions(CHANGE_CONTENT_PERMISSIONS)
        url = reverse("PageAdmin-tag_list")
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                "<title>PyLucid - lucidTag list</title>",

                "<caption>list of all existing lucidTags</caption>",
                "value='&#x7B;% lucidTag auth %&#x7D;'",
                "value='&#x7B;% lucidTag language %&#x7D;'",

                "context keys",
                "<li>&#x7B;&#x7B; current_site &#x7D;&#x7D;</li>",
                "<li>&#x7B;&#x7B; page_title &#x7D;&#x7D;</li>",
                "<li>&#x7B;&#x7B; user &#x7D;&#x7D;</li>",
            ),
            must_not_contain=(
                "XXX INVALID TEMPLATE STRING", "Traceback",
                "wrong tag example"
            )
        )

    def test_translate_form(self):
        self.login("superuser")
        url = reverse("PageAdmin-translate", kwargs={"pagemeta_id":1})
        response = self.client.get(url)

        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        csrf_token = csrf_cookie.value

        # XXX: work-a-round for: https://github.com/gregmuellegger/django/issues/1
        response.content = response.content.replace(
            """.before('<h2 class="ajax_msg">submit...</h2>');""",
            """.before('submit...');""",
        )
        response.content = response.content.replace(
            """.html('<h2 class="noanchor">loading...</h2>');""",
            """.html('loading...');"""
        )
        self.assertDOM(response,
            must_contain=(
                "<title>PyLucid - Translate page &#39;welcome&#39; (English) into Deutsch.</title>",
                "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % csrf_token,
                '<input type="submit" name="save" value="Save" />',
                '<input type="submit" name="cancel" value="Cancel" />'
            )
        )
        self.assertResponse(response,
            must_contain=(
                "Translate page &#39;welcome&#39; (English) into Deutsch.",
                '<a href="/pylucid_admin/plugins/page_admin/markup_help/"',
                '<a href="/pylucid_admin/plugins/page_admin/page_list/"',
                '<a href="/pylucid_admin/plugins/page_admin/tag_list/"',

                '>Welcome to your fesh PyLucid CMS installation ;)',
                '>Willkommen auf deiner frisch installierem PyLucid CMS Seiten ;)',
                '{% lucidTag update_journal %}</textarea>',
            ),
            must_not_contain=("XXX INVALID TEMPLATE STRING", "Traceback", "Form errors", "field is required")
        )

    def test_rename_slug(self):
        pagetree = PageTree.objects.get(slug="example-pages")
        response = self.client.get("/en/SiteMap/")
        self.assertResponse(response,
            must_contain=(
                "/en/example-pages/",
            ),
            must_not_contain=("XXX INVALID TEMPLATE STRING", "Traceback")
        )
        pagetree.slug = "new-slug"
        pagetree.save()
        response = self.client.get("/en/SiteMap/")
        self.assertResponse(response,
            must_contain=(
                "/en/new-slug/",
            ),
            must_not_contain=(
                "XXX INVALID TEMPLATE STRING", "Traceback",
                "/en/example-pages/"
            )
        )


class PageAdminHelperViewsTest(PageAdminTestCase):

    def test_markup_help(self):
        self.login("superuser")
        url = reverse("PageAdmin-markup_help")
        url += "?markup_id=%s" % MARKUP_CREOLE
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                "<title>PyLucid - creole markup help</title>",
                '<option value="6" selected="selected">Creole wiki markup</option>',
                "creole_cheat_sheet.png",
                "creole macros",
            ),
            must_not_contain=(
                "XXX INVALID TEMPLATE STRING", "Traceback",
                "errorlist", "This field is required.",
            )
        )

    def test_page_list(self):
        self.login("superuser")
        url = reverse("PageAdmin-page_list")
        url += "?markup_id=%s" % MARKUP_CREOLE
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                "<title>PyLucid - page list</title>",
                '<option value="6" selected="selected">Creole wiki markup</option>',
                "list of all accessable pages",
                "value='[[/permalink/1/welcome-to-your-pylucid-cms-|Welcome to your PyLucid CMS =;-)]]'",
            ),
            must_not_contain=(
                "XXX INVALID TEMPLATE STRING", "Traceback",
                "errorlist", "This field is required.",
            )
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
        self.assertStatusCode(response, 200)

        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        csrf_token = csrf_cookie.value

        # XXX: work-a-round for: https://github.com/gregmuellegger/django/issues/1
        response.content = response.content.replace(
            """.before('<h2 class="ajax_msg">submit...</h2>');""",
            """.before('submit...');""",
        )
        response.content = response.content.replace(
            """.html('<h2 class="ajax_msg">loading...</h2>');""",
            """.html('loading...');"""
        )

        self.assertDOM(response,
            must_contain=(
                '<div id="edit_page_preview"></div>',
                "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % csrf_token,
                '<input type="submit" name="save" value="Save" />',
                '<input type="submit" id="submit_preview" name="preview" value="markup preview" />',
                '<button type="button" id="ajax_preview" title="markup preview">markup preview</button>',
                '<label for="id_content"><strong>Content</strong>:</label>',
            )
        )
        self.assertResponse(response,
            must_contain=(
                "Edit the CMS page '<strong>Welcome to your PyLucid CMS =;-)</strong>'",
                '&#x7B;% lucidTag update_journal %&#x7D;</textarea>', # PageContent
                # CSS:
                '#ajax_preview {',
                # JavaScript:
                '$("#ajax_preview").show();',
                # Some form strings:
                'form action="/?page_admin=inline_edit"',
                '&#x7B;% lucidTag update_journal %&#x7D;</textarea>',
            ),
            must_not_contain=(
                "XXX INVALID TEMPLATE STRING",
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
        self.assertStatusCode(response, 200)
        self.failUnlessEqual(
            response.content,
            '<p>A <strong>creole</strong> <i>preview</i>!</p>'
        )


class ConvertMarkupTest(basetest.BaseLanguageTestCase):

    def _pre_setup(self, *args, **kwargs):
        """ create some language related attributes """
        super(ConvertMarkupTest, self)._pre_setup(*args, **kwargs)

        self.pagecontent = PageContent.objects.all().filter(markup=MARKUP_TINYTEXTILE)[0]
        self.pagetree = PageTree.on_site.get(pagemeta=self.pagecontent.pagemeta)
        self.url = reverse("PageAdmin-convert_markup", kwargs={"pagecontent_id":self.pagecontent.id})

        self.login("superuser")

    def setUp(self):
        super(ConvertMarkupTest, self).setUp()
        self._OLD_COMPRESS = settings.COMPRESS_ENABLED
        settings.COMPRESS_ENABLED = False

    def tearDown(self):
        super(ConvertMarkupTest, self).tearDown()
        settings.COMPRESS_ENABLED = self._OLD_COMPRESS

    def test_get_convert_form(self):
        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=(
                "<title>PyLucid - Convert &#39;tinyTextile&#39; markup</title>",
                "<input type='hidden' name='csrfmiddlewaretoken' value='",
                'The original markup is: <strong>tinytextile</strong>',
                'h1. headlines',
            ),
            must_not_contain=(
                "XXX INVALID TEMPLATE STRING", "Traceback", 'Permission denied',
            ),
        )

    def test_convert_verbose_preview(self):
        response = self.client.post(self.url, data={
            'content': '* 1.\n** 1.1.',
            'dest_markup': MARKUP_CREOLE,
            'preview': 'Vorschau',
            'verbose': 'on'
        })
        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        csrf_token = csrf_cookie.value

        # XXX: work-a-round for: https://github.com/gregmuellegger/django/issues/1
        response.content = response.content.replace(
            """.html('<h2 class="noanchor">loading...</h2>');""",
            """.html('loading...');"""
        )

        self.assertDOM(response,
            must_contain=(
                "<title>PyLucid - Convert &#39;tinyTextile&#39; markup</title>",
                "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % csrf_token,
                '<legend class="pygments_code">Diff</legend>',
                '<span class="gd">- &lt;li&gt;1.&lt;/li&gt;</span>',
                '<span class="gi">+ &lt;li&gt;1.</span>',
                '<legend>new markup</legend>',
                '<pre>* 1.\n** 1.1.</pre>',
                '<textarea cols="40" id="id_content" name="content" rows="10">* 1.\n** 1.1.</textarea>',
            )
        )
        self.assertResponse(response,
            must_contain=(
                # Real pygments CSS content is removed in unittests!
                # more info in pylucid_project/tests/test_tools/basetest.py 
                'Pygments CSS Content',

                'The original markup is: <strong>tinytextile</strong>',
            ),
            must_not_contain=(
                "XXX INVALID TEMPLATE STRING", "Traceback", 'Permission denied',
            ),
        )

    def test_convert(self):
        response = self.client.post(self.url, data={
            'content': '* 1.\n** 1.1.',
            'dest_markup': MARKUP_CREOLE,
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
                "XXX INVALID TEMPLATE STRING", "Traceback", 'Permission denied',
            ),
        )


class BulkEditorCsrfTest(PageAdminTestCase):
    """ Test the Cross Site Request Forgery protection """
    def _get_loggedin_client(self):
        csrf_client = Client(enforce_csrf_checks=True)

        test_user = self._get_userdata("superuser")
        ok = csrf_client.login(username=test_user["username"],
                               password=test_user["password"])
        return csrf_client

    def test_csrf_token(self):
        csrf_client = self._get_loggedin_client()

        url = reverse("PageAdmin-bulk_editor")
        response = csrf_client.get(url)

        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        self.assertIsNot(csrf_cookie, False)
        csrf_token = csrf_cookie.value

        self.assertDOM(response,
            must_contain=(
                "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % csrf_token,
            ),
        )




