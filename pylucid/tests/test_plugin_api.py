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

import os, re

import tests

from django.conf import settings

from PyLucid.models import Page, Plugin
from PyLucid.system.plugin_manager import install_plugin


TEST_PLUGIN_NAME = "unittest_plugin"
CONTENT_START = "<pre>"
CONTENT_END = "</pre>"
CONTENT_RE = re.compile("<pre>(.*?)<\/pre>(?usm)")

MODEL_TEST = """<pre>
Test the plugin models
Create TestArtist
entry with ID '%(no)s' created
Create TestAlbum
entry with ID '%(no)s' created:
TestAlbum 'A test Album', ID %(no)s, createby: superuser
</pre>"""




class PluginAPI_Base(tests.TestCase):
    """
    Unit tests for detect_page function.
    """
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

    #___________________________________________________________________________
    # SHARED UTILS

    def _get_plugin_content(self, url, debug=False):
        """
        request the url and returns the plugin content output
        """
        response = self.client.get(url)
        # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)

        raw_content = response.content
        if debug:
            print "-"*79
            print raw_content
            print "-"*79

        content = CONTENT_RE.findall(raw_content)
        if len(content) == 1:
            return content[0].strip()

        msg = (
            "Content not found in:\n"
            "----------------------------------------------------------------\n"
            "%s"
            "----------------------------------------------------------------"
        ) % raw_content
        self.fail(msg)

    def _get_plugin(self):
        return Plugin.objects.get(plugin_name=TEST_PLUGIN_NAME)

    #___________________________________________________________________________
    # PRETESTS

    def test_plugin_exist(self):
        """
        Test if the unittest plugin is normal installed and active
        """
        try:
            self.plugin = self._get_plugin()
        except Plugin.DoesNotExist, err:
            self.fail("Plugin doesn't exist: %s" % err)

        self.failUnless(self.plugin.active, True)
        #print "Plugin exists ID:", self.plugin.id

    def test_hello_world(self):
        """
        Checks via _command url the hello world response
        """
        url = self.command % "hello_world"
        response = self.client.get(url)
        # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual2(
            response.content.strip(),
            (
                '<div class="PyLucidPlugins unittest_plugin"'
                ' id="unittest_plugin_hello_world">\n'
                'Hello world!\n'
                '</div>'
            )
        )


class PluginModel(PluginAPI_Base):
    """
    Tests around the plugin models.
    """
    def test_plugin_models(self):
        """
        Test the plugin models.
        Request three times the plugin_models view. This view creates on
        every request a new model entry in both test models and display
        some informations around this.
        After this, we request a view with a list of all existing model entries.
        """
        self.login("superuser") # login client as superuser

        url = self.command % "plugin_models"

        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            MODEL_TEST % {"no": 1}
        )

        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            MODEL_TEST % {"no": 2}
        )

        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            MODEL_TEST % {"no": 3}
        )

        # Test all models view: A list of all existing models.
        url = self.command % "all_models"
        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            (
                "<pre>\n"
                "All Albums:\n"
                "1: TestAlbum 'A test Album', ID 1, createby: superuser\n"
                "2: TestAlbum 'A test Album', ID 2, createby: superuser\n"
                "3: TestAlbum 'A test Album', ID 3, createby: superuser\n"
                "</pre>"
            )
        )

    def test_reinit(self):
        """
        reinit the plugin and check if the plugin model tabels would be
        droped and re-created.
        """
        plugin = self._get_plugin()
        
        package_name = plugin.package_name
        plugin_name = plugin.plugin_name
        
        # remove the plugin completely from the database
        # plugin model tables should be droped
        plugin.delete()
        
        # install the plugin
        # plugin model tables should be re-created, too. 
        install_plugin(package_name, plugin_name, debug=True, active=True,
                                                        extra_verbose=True)

        # Check 1:
        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            MODEL_TEST % {"no": 1}
        )

        # Check 2:
        url = self.command % "all_models"
        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            (
                "<pre>\n"
                "All Albums:\n"
                "1: TestAlbum 'A test Album', ID 1, createby: superuser\n"
                "</pre>"
            )
        )


class PluginModel(PluginAPI_Base):
    """
    pass parameters to the plugin method.
    """
    def test_lucidTag(self):
        content = self._get_plugin_content(self.test_url)
        self.assertEqual2(content, "args:\n()\npformarted kwargs:\n{}")

    def test_plugin_args1(self):
        """
        Test arguments in the lucidTag
        Handled in PyLucid.template_addons.lucidTag
        """
        def get_args_info(page_content):
            self.test_page.content = page_content
            self.test_page.save()
            content = self._get_plugin_content(self.test_url, debug=False)
            args_info = content.split("\n")
            return (args_info[1], args_info[3])


        args, kwargs = get_args_info('{% lucidTag unittest_plugin %}')
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs, "{}")


        args, kwargs = get_args_info(
            '{% lucidTag unittest_plugin arg1="test1" %}'
        )
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs, "{'arg1': u'test1'}")


        args, kwargs = get_args_info(
            '{% lucidTag unittest_plugin a="0" b="1" c="2" %}'
        )
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs, "{'a': u'0', 'b': u'1', 'c': u'2'}")


        args, kwargs = get_args_info(
            '{% lucidTag unittest_plugin'
            ' t1="True" f1="False" t2="true" f2="false" %}'
        )
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs, 
            "{'f1': False, 'f2': False, 't1': True, 't2': True}"
        )

    def test_plugin_args2(self):
        """
        Test arguments in a _command url
        """
        url = self.command % "lucidTag"
        url += "some/stuff/here/1/2/3/"
        content = self._get_plugin_content(url, debug=False)
        self.assertEqual2(
            content,
            "args:\n"
            "(u'some/stuff/here/1/2/3/',)\n"
            "pformarted kwargs:\n"
            "{}"
        )



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])