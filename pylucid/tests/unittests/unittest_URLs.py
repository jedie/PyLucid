#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test PyLucid.tools.crypt

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from setup_environment import setup, get_fake_context
setup(
    path_info=False, extra_verbose=False,
    syncdb=False, insert_dump=False,
    install_plugins=False
)

#______________________________________________________________________________
# Test:

import os, unittest

from django.conf import settings

from PyLucid.system.URLs import URLs





class TestBase(unittest.TestCase):
    def setUp(self):
        context = get_fake_context()
        self.URLs = URLs(context)

    def test_asserts(self):
        """
        Check the defaults
        """
#        self.URLs.debug()
        self.assertEqual(
            self.URLs["adminBase"], "/%s" % settings.ADMIN_URL_PREFIX
        )
        self.assertEqual(
            self.URLs["hostname"], "http://unitest_HTTP_HOST_fake"
        )
        self.assertEqual(self.URLs["scriptRoot"], "/")
        self.assertEqual(self.URLs["host"], "unitest_HTTP_HOST_fake")
        self.assertEqual(
            self.URLs["absoluteIndex"], "http://unitest_HTTP_HOST_fake/"
        )
        self.assertEqual(self.URLs["docRoot"], "/")
        self.assertEqual(self.URLs["cwd"], os.getcwdu())

    def test_command_base(self):
        self.assertEqual(
            self.URLs.get_command_base(), "/%s/1" % settings.COMMAND_URL_PREFIX
        )

    def test_commandLink(self):
        prefix = "/%s/1" % settings.COMMAND_URL_PREFIX
        self.assertEqual(
            self.URLs.commandLink("plugin_name", "method_name"),
            "%s/plugin_name/method_name/" % prefix
        )
        self.assertEqual(
            self.URLs.commandLink(
                "plugin_name", "method_name", args="parm1"
            ),
            "%s/plugin_name/method_name/parm1/" % prefix
        )
        self.assertEqual(
            self.URLs.commandLink(
                "plugin_name", "method_name", args=("parm1", "parm2")
            ),
            "%s/plugin_name/method_name/parm1/parm2/" % prefix
        )
        self.assertEqual(
            self.URLs.commandLink(
                "plugin_name", "method_name", args=["parm1", "parm2"]
            ),
            "%s/plugin_name/method_name/parm1/parm2/" % prefix
        )
        self.assertEqual(
            self.URLs.commandLink(
                "plugin_name", "method_name", args=1
            ),
            "%s/plugin_name/method_name/1/" % prefix
        )
        self.assertEqual(
            self.URLs.commandLink(
                "plugin_name", "method_name", args=("1",2,3)
            ),
            "%s/plugin_name/method_name/1/2/3/" % prefix
        )
        

    def test_methodLink(self):
        prefix = "/%s/1/plugin_name" % settings.COMMAND_URL_PREFIX
        self.URLs.current_plugin = "plugin_name"
        self.assertEqual(
            self.URLs.methodLink("method_name"),
            "%s/method_name/" % prefix
        )
        self.assertEqual(
            self.URLs.methodLink("method_name", args="parm1"),
            "%s/method_name/parm1/" % prefix
        )
        self.assertEqual(
            self.URLs.methodLink("method_name", args=["parm1", "parm2"]),
            "%s/method_name/parm1/parm2/" % prefix
        )
        
    def test_adminLink(self):
        prefix= "/%s" % settings.ADMIN_URL_PREFIX
        self.assertEqual(
            self.URLs.adminLink("test1"),
            "%s/test1/" % prefix
        )
        self.assertEqual(
            self.URLs.adminLink([1,2,3]),
            "%s/1/2/3/" % prefix
        )
        
    def test_make_absolute_url(self):
        prefix = self.URLs["hostname"]
        self.assertEqual(
            self.URLs.make_absolute_url("test1"),
            "%s/test1/" % prefix
        )
        self.assertEqual(
            self.URLs.make_absolute_url(["test1", "test2"]),
            "%s/test1/test2/" % prefix
        )
        
        


if __name__ == "__main__":
    print
    print ">>> Unitest: PyLucid.system.URLs"
    print
    print "Note the URLs.py has some DocTests, too ;)"
    print
    print "_"*79
    unittest.main()
