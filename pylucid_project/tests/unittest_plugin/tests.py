#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" blog entry in english and german
    
    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import os
import logging
import sys

if __name__ == "__main__":
    # Run all unittest directly

    tests = __file__
#    tests = "pylucid_project.pylucid_plugins.unittest_plugin.tests"
#    tests = "pylucid_project.pylucid_plugins.unittest_plugin.tests.UnittestPluginCsrfTests"
#    tests = "pylucid_project.pylucid_plugins.unittest_plugin.tests.TestUnitestPlugin.test_if_plugin_exists"
#    tests = "pylucid_project.pylucid_plugins.unittest_plugin.tests.TestUnitestPluginPage"

    from pylucid_project.tests import run_test_directly
    run_test_directly(tests,
        verbosity=2,
#        failfast=True,
        failfast=False,
    )
    sys.exit()

from django.conf import settings
from django.contrib.messages import constants as message_constants
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils.log import getLogger

from pylucid_project.apps.pylucid.preference_forms import SystemPreferencesForm
from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS
from pylucid_project.tests.test_tools import basetest

#logger = getLogger("pylucid.unittest_plugin")
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())

class TestUnitestPlugin(basetest.BaseUnittest):
    """
    inherited from BaseUnittest:
        - initial data fixtures with default test users
        - self.login()
    """
    def test_if_exist_in_pylucid_plugins_data(self):
        self.failUnless("unittest_plugin" in PYLUCID_PLUGINS)

    def test_if_plugin_exists(self):
        self.login("superuser")
        response = self.client.get("/pylucid_admin/plugins/internals/show_internals/")
        self.assertResponse(response,
            must_contain=(
                "pylucid_project.pylucid_plugins.unittest_plugin", #INSTALLED_APPS
                "/PyLucid_env/src/pylucid/pylucid_project/tests/unittest_plugin", # sys.path 
            ),
            must_not_contain=("Traceback",)
        )

    def test_anonymous(self):
        cache.clear() # page message can be only see, if cache not used!
        response = self.client.get("/en/welcome/?unittest_plugin=MSG_ERROR")
#        response = self.client.get("/pylucid_admin/plugins/internals/show_internals/")
        self.assertResponse(response,
            must_contain=("<html", "A error messages"),
            must_not_contain=("Traceback",)
        )

class TestUnitestPluginPage(basetest.BaseUnittest):

    def _pre_setup(self, *args, **kwargs):
        super(TestUnitestPluginPage, self)._pre_setup(*args, **kwargs)

        self.login("superuser")

        new_plugin_page_url = reverse("PageAdmin-new_plugin_page")
        test_slug = "ut_plugin"
        response = self.client.post(new_plugin_page_url,
            data={'app_label': 'pylucid_project.pylucid_plugins.unittest_plugin',
            'design': 1,
            'position': 0,
            'slug': test_slug,
            'urls_filename': 'urls.py'
            }
        )
        self.url = "http://testserver/en/%s/" % test_slug
        self.assertRedirect(response, self.url, status_code=302)

        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=("New plugin page", "unittest_plugin", "created."),
            must_not_contain=("Traceback",)
        )

    def tearDown(self):
        super(TestUnitestPluginPage, self).tearDown()
        settings.DEBUG = False

    def test_plugin_page(self):
        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=("String response from pylucid_plugins.unittest_plugin.view_root()",),
            must_not_contain=("Traceback",)
        )

    def test_messages(self):
        response = self.client.get(self.url + "test_messages/")
        self.assertResponse(response,
            must_contain=(
                "Response from unittest_plugin.test_messages()",
                "A &#39;debug&#39; message",
                "A &#39;info&#39; message",
                "A &#39;success&#39; message",
                "A &#39;warning&#39; message",
                "A &#39;error&#39; message",
            ),
            must_not_contain=("Traceback",)
        )

    def test_cache(self):
        url = self.url + "test_cache/"
        client = Client()

        # put page to cache with [one]
        client.cookies["test_messages"] = "one"
        response = client.get(url)
        self.assertResponse(response,
            must_contain=(
                "Response from unittest_plugin.test_cache() [one]",
            ),
            must_not_contain=("Traceback",)
        )
        self.assertFalse(response._from_cache)

        # request page from cache, so not [two] -> old content with [one]
        client.cookies["test_messages"] = "two"
        response = client.get(url)
        self.assertResponse(response,
            must_contain=(
                "Response from unittest_plugin.test_cache() [one]",
            ),
            must_not_contain=("Traceback",)
        )
        self.assertTrue(response._from_cache)

    def test_non_caching_pages_with_messages(self):
        system_preferences = SystemPreferencesForm()
        system_preferences["message_level_anonymous"] = message_constants.DEBUG
        system_preferences.save()

        url = self.url + "test_messages/"
        client = Client()

        # Put page into cache?
        client.cookies["test_messages"] = "one"
        response = client.get(url)
        self.assertResponse(response,
            must_contain=(
                "Response from unittest_plugin.test_messages() [one]",
                "A &#39;debug&#39; message",
                "A &#39;info&#39; message",
                "A &#39;success&#39; message",
                "A &#39;warning&#39; message",
                "A &#39;error&#39; message",
            ),
            must_not_contain=("Traceback",)
        )
        self.assertFalse(response._from_cache)

        # Request from cache?
        client.cookies["test_messages"] = "two"
        response = client.get(url)
        self.assertResponse(response,
            must_contain=(
                "Response from unittest_plugin.test_messages() [two]",
                "A &#39;debug&#39; message",
                "A &#39;info&#39; message",
                "A &#39;success&#39; message",
                "A &#39;warning&#39; message",
                "A &#39;error&#39; message",

            ),
            must_not_contain=("Traceback",)
        )
        self.assertFalse(response._from_cache)

    def test_MessageLevelMiddleware(self):
        url = self.url + "test_messages/"
        client = Client()
        system_preferences = SystemPreferencesForm()

        def get_response(level):
            system_preferences["message_level_anonymous"] = level
            system_preferences.save()
            return client.get(url)

        self.assertResponse(get_response(message_constants.DEBUG),
            must_contain=(
                "Response from unittest_plugin.test_messages()",
                "A &#39;debug&#39; message",
                "A &#39;info&#39; message",
                "A &#39;success&#39; message",
                "A &#39;warning&#39; message",
                "A &#39;error&#39; message",
            ),
            must_not_contain=("Traceback",)
        )

        self.assertResponse(get_response(message_constants.INFO),
            must_contain=(
                "Response from unittest_plugin.test_messages()",
                "A &#39;info&#39; message",
                "A &#39;success&#39; message",
                "A &#39;warning&#39; message",
                "A &#39;error&#39; message",
            ),
            must_not_contain=("Traceback",
                "A &#39;debug&#39; message",
            )
        )

        self.assertResponse(get_response(message_constants.SUCCESS),
            must_contain=(
                "Response from unittest_plugin.test_messages()",
                "A &#39;success&#39; message",
                "A &#39;warning&#39; message",
                "A &#39;error&#39; message",
            ),
            must_not_contain=("Traceback",
                "A &#39;info&#39; message",
                "A &#39;debug&#39; message",
            )
        )

        self.assertResponse(get_response(message_constants.WARNING),
            must_contain=(
                "Response from unittest_plugin.test_messages()",
                "A &#39;warning&#39; message",
                "A &#39;error&#39; message",
            ),
            must_not_contain=("Traceback",
                "A &#39;success&#39; message",
                "A &#39;info&#39; message",
                "A &#39;debug&#39; message",
            )
        )

        self.assertResponse(get_response(message_constants.ERROR),
            must_contain=(
                "Response from unittest_plugin.test_messages()",
                "A &#39;error&#39; message",
            ),
            must_not_contain=("Traceback",
                "A &#39;warning&#39; message",
                "A &#39;success&#39; message",
                "A &#39;info&#39; message",
                "A &#39;debug&#39; message",
            )
        )


class UnittestPluginCsrfTests(basetest.BaseUnittest):
    def _pre_setup(self, *args, **kwargs):
        super(UnittestPluginCsrfTests, self)._pre_setup(*args, **kwargs)

        self.login("superuser")

        new_plugin_page_url = reverse("PageAdmin-new_plugin_page")
        test_slug = "ut_plugin"
        response = self.client.post(new_plugin_page_url,
            data={'app_label': 'pylucid_project.pylucid_plugins.unittest_plugin',
            'design': 1,
            'position': 0,
            'slug': test_slug,
            'urls_filename': 'urls.py'
            }
        )
        self.url = "http://testserver/en/%s/" % test_slug
        self.assertRedirect(response, self.url, status_code=302)

        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=("New plugin page", "unittest_plugin", "created."),
            must_not_contain=("Traceback",)
        )

        self.csrf_client = Client(enforce_csrf_checks=True)
        test_user = self._get_userdata("superuser")
        self.csrf_client.login(
            username=test_user["username"], password=test_user["password"]
        )

    def request_csrf_token(self, url):
        response = self.csrf_client.get(url)
        self.assertResponse(response,
            must_contain=("<input type='hidden' name='csrfmiddlewaretoken' value='",),
            must_not_contain=()
        )
        csrf_cookie = response.cookies.get(settings.CSRF_COOKIE_NAME, False)
        csrf_token = csrf_cookie.value
        return csrf_token

    #--------------------------------------------------------------------------

    def test_get_csrf_exempt_view(self):
        response = self.csrf_client.get(self.url + "csrf_exempt_view/")
        self.assertResponse(response,
            must_contain=("<dt>view name</dt><dd>csrf_exempt_view()</dd>",),
            must_not_contain=("Traceback",)
        )

    def test_post_csrf_exempt_view(self):
        response = self.csrf_client.post(self.url + "csrf_exempt_view/")
        self.assertResponse(response,
            must_contain=("<dt>view name</dt><dd>csrf_exempt_view()</dd>",),
            must_not_contain=("Traceback",)
        )

    #--------------------------------------------------------------------------

    def test_get_csrf_no_decorator_view(self):
        response = self.csrf_client.get(self.url + "csrf_no_decorator_view/")
        self.assertResponse(response,
            must_contain=("<dt>view name</dt><dd>csrf_no_decorator_view()</dd>",),
            must_not_contain=("Traceback",)
        )

    def test_post_csrf_no_decorator_view_without_token(self):
        response = self.csrf_client.post(self.url + "csrf_no_decorator_view/")
        self.assertResponse(response,
            must_contain=("CSRF verification failed. Request aborted.",),
            must_not_contain=("Traceback",)
        )
        self.assertStatusCode(response, 403)

    def test_post_csrf_no_decorator_view_with_token(self):
        # get the current csrf token
        csrf_token = self.request_csrf_token(self.url + "csrf_no_decorator_view/")

        response = self.csrf_client.post(
            self.url + "csrf_no_decorator_view/",
            data={"csrfmiddlewaretoken": csrf_token}
        )
        self.assertResponse(response,
            must_contain=(
                "<dt>view name</dt><dd>csrf_no_decorator_view()</dd>",
                '<dt>request.POST["csrfmiddlewaretoken"]</dt><dd>%s</dd>' % csrf_token,
            ),
            must_not_contain=("Traceback",)
        )

    #--------------------------------------------------------------------------

    def test_get_csrf_in_get_view(self):
        response = self.csrf_client.get("/en/welcome/?unittest_plugin=csrf_test")
        self.assertResponse(response,
            must_contain=("<dt>view name</dt><dd>csrf get view</dd>",),
            must_not_contain=("Traceback",)
        )

    def test_post_csrf_in_get_view_without_token(self):
        response = self.csrf_client.post("/en/welcome/?unittest_plugin=csrf_test")
        self.assertResponse(response,
            must_contain=("CSRF verification failed. Request aborted.",),
            must_not_contain=("Traceback",)
        )
        self.assertStatusCode(response, 403)

    def test_post_csrf_in_get_view_with_token(self):
        # get the current csrf token
        csrf_token = self.request_csrf_token("/en/welcome/?unittest_plugin=csrf_test")

        # send a POST with csrf token
        response = self.csrf_client.post(
            "/en/welcome/?unittest_plugin=csrf_test",
            data={"csrfmiddlewaretoken": csrf_token}
        )
        self.assertResponse(response,
            must_contain=(
                "<dt>view name</dt><dd>csrf get view</dd>",
                '<dt>request.POST["csrfmiddlewaretoken"]</dt><dd>%s</dd>' % csrf_token,
            ),
            must_not_contain=("Traceback",)
        )


