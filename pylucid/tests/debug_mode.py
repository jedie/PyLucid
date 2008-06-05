#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    PyLucid tying to help debugging, but anonymous user should never see any
    debug info (e.g. Traceback). This unittest should verify that.

    It's not a test for the user permission generally!
    We have some seperate tests for this case, e.g.:
        .../tests/test_plugin_manager.py

    There exist two bool variables that define whether debugging is on or off:
        - settings.DEBUG
        - request.debug

    settings.DEBUG
        is the normal django variable set in settings.py:
        http://www.djangoproject.com/documentation/settings/#debug

    request.debug
        is a PyLucid own variable. It's true if settings.DEBUG if True or the
        client IP address is in settings.INTERNAL_IPS.
        The variable set in PyLucid.system.utils.setup_debug()

    All PyLucid parts should use request.debug intend of settings.DEBUG.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import unittest, sys, re, os, time

import tests
from tests import TEST_USERS
from tests.utils.BrowserDebug import debug_response

from django.conf import settings

from PyLucid.system.exceptions import *
from PyLucid.models import Plugin

# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True


class TestBase(tests.TestCase):
    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    def setUp(self):
        self.base_url = "/%s/1" % settings.COMMAND_URL_PREFIX



class NotLoginTest(TestBase):
    """
    Tests with:
     - as anonymous user
     - settings.DEBUG=False

    The normal User should not see any Debug/Traceback info.
    Exceptions should be intercepted and we see a normal page with some
    information about the error.

    If a django.http.Http404 exception raised, the user should see the PyLucid
    own 404 page instead of the the django 404 page.
    """
    def setUp(self):
        super(NotLoginTest, self).setUp()
        settings.DEBUG=False

    def test_wrong_plugin(self):
        """
        _command url with a not existing plugin.
        -> Exception Plugin.DoesNotExist raised in plugin_manager
        """
        url = self.base_url + "/wrong_plugin/wrong_method/"
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response, must_contain=(
                "Error run plugin", "Plugin not exists in database",
            )
        )

    def test_wrong_method(self):
        """
        _command url with a existing plugin, but a wrong method
        -> The plugin_manager raised a KeyError
        """
        url = self.base_url + "/auth/wrong_method/"
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response, must_contain=(
                "Error run plugin", "Can't get config for the method",
            )
        )

    def test_AccessDenied(self):
        """
        The anonymous user try to edit a page.
        -> The plugin manager raised AccessDenied.
        """
        url = self.base_url + "/page_admin/edit_page/"
        response = self.client.get(url)
        #debug_response(response)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("[Permission Denied!]",),
            must_not_contain=("Traceback",)
        )

    def test_page_msg(self):
        """
        Test the debug modus in page_msg.
        Here we should not see, the information who the page_msg created.
        """
        url = self.base_url + "/auth/login/"
        response = self.client.post(url, {})
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=("Form data is not valid. Please correct.",),
            must_not_contain=("/auth/auth.py line",)
        )

    #__________________________________________________________________________
    # 404 tests

    def test_wrong_cms_page(self):
        """
        request a not existing cms page
        -> django.http.Http404 should be raised
        """
        self.assertPyLucid404(url = "/NotExistingPage")

    def test_Http404(self):
        """
        The anonymous user try to get a not existing Stylesheet.
        -> The page_style Plugin raised django.http.Http404
        """
        url = self.base_url + "/page_style/sendStyle/NotExistsStyle.css"
        self.assertPyLucid404(url)




class TestDebugMsg(TestBase):
    """
    Tests with:
     - as anonymous user
     - settings.DEBUG=True

    In DEBUG mode, any error should response Debug/Traceback information.
    Exception should not be intercepted.
    """
    def setUp(self):
        super(TestDebugMsg, self).setUp()
        settings.DEBUG=True

    def test_wrong_plugin(self):
        """
        _command url with a not existing plugin.
        -> Exception Plugin.DoesNotExist raised in plugin_manager
        """
        url = self.base_url + "/wrong_plugin/wrong_method/"
        self.assertRaises(Plugin.DoesNotExist, self.client.get, url)

    def test_wrong_method(self):
        """
        _command url with a existing plugin, but a wrong method
        -> The plugin_manager raised a KeyError
        """
        url = self.base_url + "/auth/wrong_method/"
        self.assertRaises(KeyError, self.client.get, url)

    def test_AccessDenied(self):
        """
        The anonymous user try to edit a page.
        -> The plugin manager raised AccessDenied.
        """
        url = self.base_url + "/page_admin/edit_page/"
        self.assertRaises(AccessDenied, self.client.get, url)

    def test_page_msg(self):
        """
        Test the debug modus in page_msg.
        Here we should see, the information who the page_msg created, e.g:
        ...ins_internal/auth/auth.py line 183: Form data is not valid...
        """
        url = self.base_url + "/auth/login/"
        response = self.client.post(url, {})
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response,
            must_contain=(
                "Form data is not valid. Please correct.",
                "/auth/auth.py line"
            ),
        )

    #__________________________________________________________________________
    # 404 tests

    def test_wrong_cms_page(self):
        """
        request a not existing cms page
        -> django.http.Http404 should be raised
        """
        self.assertDjango404(url = "/NotExistingPage")

    def test_Http404(self):
        """
        The anonymous user try to get a not existing Stylesheet.
        -> The page_style Plugin raised django.http.Http404
        In DEBUG mode, the django 404 Page should be response
        """
        url = self.base_url + "/page_style/sendStyle/NotExistsStyle.css"
        self.assertDjango404(url)




if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])