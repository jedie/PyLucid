#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Try to test the ./PyLucid/urls.py re patterns.

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

from django.core.urlresolvers import reverse, RegexURLResolver, NoReverseMatch


class TestURLpatterns_reverse_test(unittest.TestCase):
    """
    reverse test
    ~~~~~~~~~~~~
    Test the url re patterns via django.core.urlresolvers.reverse
    """

    def test_reverse_admin(self):
        """
        'django.contrib.admin.urls'
        """
        self.assertEqual(
            reverse('django.contrib.admin.views.main.index'),
            "/%s/" % settings.ADMIN_URL_PREFIX
        )

    def test_reverse_command(self):
        """
        _command url
        """
        self.assertRaises(
            NoReverseMatch, reverse, 'PyLucid.index.handle_command'
        )
        self.assertEqual(
            reverse(
                'PyLucid.index.handle_command',
                args=[1,"module_name", "method_name", "url_args"]
            ),
            "/%s/1/module_name/method_name/url_args" % \
                                                    settings.COMMAND_URL_PREFIX
        )

    def test_reverse_permalink(self):
        """
        permalink url
        """
        self.assertRaises(NoReverseMatch, reverse, 'PyLucid.index.permalink')
        self.assertEqual(
            reverse('PyLucid.index.permalink', args=[1,"shortcut"]),
            "/%s/1/shortcut" % settings.PERMALINK_URL_PREFIX
        )

    def test_reverse_cms_view(self):
        """
        url to a normal cms page
        """
        self.assertRaises(NoReverseMatch, reverse, 'PyLucid.index.index')
        self.assertEqual(
            reverse('PyLucid.index.index', args=["/"]), "/"
        )
        self.assertEqual(
            reverse('PyLucid.index.index', args=["shortcut"]), "/shortcut/"
        )



class TestURLpatterns(unittest.TestCase):
    """
    resolver test
    ~~~~~~~~~~~~
    Test the url re patterns via django.core.urlresolvers.RegexURLResolver
    """
    def setUp(self):
        urlconf = settings.ROOT_URLCONF
        resolver=RegexURLResolver(r'^/', urlconf)
        self.resolve = resolver.resolve

        # must be set, before the test starts
        self.module_name = None
        self.func_name = None


    def path_test(self, path):
        """
        get the function information via the RegexURLResolver.
        test if the given function is the right module and method.
        """
        view_function, function_args, function_kwargs = self.resolve(path)
        #for i in dir(view_function):
        #    try:
        #        print i, getattr(view_function, i)
        #    except:
        #        pass

        self.assertEqual(self.module_name, view_function.__module__)
        self.assertEqual(self.func_name, view_function.func_name)


    def test_cms_view(self):
        """
        url for normal cms views
        """
        self.module_name = "PyLucid.index"
        self.func_name = "index"

        self.path_test("/")
        self.path_test("/one_shortcut/")
        self.path_test("/one_shortcut/two_shortcut/")
        self.path_test("/one_shortcut/two_shortcut/tree_shortcut/")


    def test_command_url(self):
        """
        _command urls
        """
        base_path = "/%s/1/module_name/method_name/" % \
                                                settings.COMMAND_URL_PREFIX
        self.module_name = "PyLucid.index"
        self.func_name = "handle_command"

        self.path_test(base_path)
        self.path_test(base_path + "url_args")
        self.path_test(base_path + "url_args1/url_args2")
        self.path_test(base_path + "url_args1/url_args2/3/4")


    def test_install_url(self):
        """
        the _install section urls
        """
        base_path = "/%s/" % settings.INSTALL_URL_PREFIX
        self.module_name = "PyLucid.install.index"

        self.func_name = "menu"
        self.path_test(base_path)

        self.func_name = "run_method"
        self.path_test(base_path + "module_name/method_name/")
        self.path_test(base_path + "module_name/method_name/arg1/")
        self.path_test(base_path + "module_name/method_name/arg1/2")





if __name__ == "__main__":
    print
    print ">>> Unitest for the ./PyLucid/urls.py re patterns."
    print
    print "_"*79
    unittest.main()
