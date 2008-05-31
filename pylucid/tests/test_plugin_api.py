#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    unitest for plugin API
    ~~~~~~~~~~~~~~~~~~~~~~

    TODO: We can test here many other things, e.g.:
        - plugin rights
        - plugin install/activate/deactivate

    :copyleft: 2008 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import tests

from django.conf import settings

from PyLucid.models import Page, Plugin


TEST_PLUGIN_NAME = "unittest_plugin"
CONTENT_START = (
    '<div class="PyLucidPlugins unittest_plugin"'
)
CONTENT_END = "</div>"


class PluginAPI_TestCase(tests.TestCase):
    """
    Unit tests for detect_page function.
    """
#    def tearDown(self):


    def _init(self):
        print "init"
        try:
            self.plugin = Plugin.objects.get(plugin_name=TEST_PLUGIN_NAME)
        except Plugin.DoesNotExist, err:
            from PyLucid.system.plugin_manager import install_plugin
            self.plugin = install_plugin(
                package_name = "PyLucid.plugins_external",
                plugin_name = "unittest_plugin",
                debug = True,
                active=True,
                extra_verbose=True,
            )
        else:
            print "Plugin exists ID:", self.plugin.id
            
    def _delete(self):
        print "delete"
        try:
            self.plugin.delete()
        except Exception, err:
            print "tearDown Error:", err

    def setUp(self):       
        Page.objects.all().delete() # Delete all existins pages

        self.template = tests.create_template(
            content = (
                "<!-- page_messages -->\n"
                "{{ PAGE.content }}"
            )
        )

        # Create one page
        self.test_page = tests.create_page(
            content = "{% lucidTag unittest_plugin %}",
            template=self.template
        )

        self.command = "/%s/%s/%s/%%s/" % (
            settings.COMMAND_URL_PREFIX,
            self.test_page.id,
            TEST_PLUGIN_NAME,
        )
        self.test_url = self.test_page.get_absolute_url()

    def _get_plugin_content(self, url, debug=False):
        """
        request the url and returns the plugin content output
        """
        print "22222222"
        response = self.client.get(url)
        # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)

        raw_content = response.content
        if debug:
            print "-"*79
            print raw_content
            print "-"*79

        lines = raw_content.splitlines()
        in_content = False
        result = ""
        for line in lines:
            if line.startswith(CONTENT_START):
                in_content = True
                continue
            elif in_content:
                if line == CONTENT_END:
                    return result
                else:
                    result += line

        msg = (
            "Content not found in:\n"
            "----------------------------------------------------------------\n"
            "%s"
            "----------------------------------------------------------------"
        ) % raw_content
        self.fail(msg)

    def test_init_plugin(self):
        """
        First we must install the plugin
        """
        print "XXXXXXXXX"
        url = self.command % "plugin_models"
        content = self._get_plugin_content(url)


    def test_first_check(self):
        """
        Check if the test plugin exist and is active
        """
#        self._init()
        try:
            plugin = Plugin.objects.get(plugin_name=TEST_PLUGIN_NAME)
        except Plugin.DoesNotExist, err:
            self.fail("test plugin doesn't exist in the database: %s" % err)

        self.failUnless(plugin.active, True)
        
#        self._delete()

    def test_hello_world(self):
        """
        Checks via _command url the hello world response
        """
        url = self.command % "hello_world"
        content = self._get_plugin_content(url)
        self.assertEqual(content, "Hello world!")

    def test_lucidTag(self):
        content = self._get_plugin_content(self.test_url)
        self.assertEqual(content, "args: (), kwargs: {}")

    def test_plugin_args1(self):
        """
        Test arguments in a _command url
        """
        content = self._get_plugin_content(self.test_url, debug=False)
        self.assertEqual(
            content, "args: (), kwargs: {}"
        )

        self.test_page.content = '{% lucidTag unittest_plugin arg1="test1" %}'
        self.test_page.save()
        content = self._get_plugin_content(self.test_url, debug=False)
        self.assertEqual(
            content, "args: (), kwargs: {'arg1': u'test1'}"
        )

        self.test_page.content = '{% lucidTag unittest_plugin arg1=True %}'
        self.test_page.save()
        content = self._get_plugin_content(self.test_url, debug=True)
        self.assertEqual(
            content, "args: (), kwargs: {'arg1': True}"
        )

    def test_plugin_args2(self):
        """
        Test arguments in a _command url
        """
        url = self.command % "lucidTag"
        url += "some/stuff/here/1/2/3/"
        content = self._get_plugin_content(url, debug=False)
        self.assertEqual(
            content, "args: (u'some/stuff/here/1/2/3/',), kwargs: {}"
        )



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])