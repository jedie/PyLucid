#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Try to test the ./PyLucid/urls.py re patterns.

    Limits
    ~~~~~~
    Some tests depents on these settings:
        settings.ENABLE_INSTALL_SECTION
        settings.SERVE_STATIC_FILES
    To run all tests, we must switch these variables and reinit django.
    You can run these test script standalone and switch the variable here, see
    settings import down.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, unittest

if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "pylucid.tests.testutils.settings"

from django.conf import settings

from django.core.urlresolvers import reverse, RegexURLResolver, NoReverseMatch


class TestWithReverse(unittest.TestCase):
    """
    reverse test
    ~~~~~~~~~~~~
    Test the url re patterns via django.core.urlresolvers.reverse
    """
    def test_root_page(self):
        self.failUnlessEqual(reverse('PyLucid-root_page'), "/")
        
    def test_resolve_url(self):
        self.failUnlessEqual(reverse('PyLucid-resolve_url', kwargs={'lang_code': 'de', 'url_path': 'slug'}),
            "/de/slug/")
        self.failUnlessEqual(reverse('PyLucid-resolve_url', kwargs={'lang_code': 'de-at', 'url_path': 'slug'}),
            "/de-at/slug/")
        self.failUnlessEqual(reverse('PyLucid-resolve_url', kwargs={'lang_code': 'de_at', 'url_path': 'slug'}),
            "/de_at/slug/")
        
    def test_existing_lang(self):
        self.failUnlessEqual(reverse('PyLucid-existing_lang', kwargs={'url_path': 'slug1/slug2'}),
            "/slug1/slug2/")
        
        
        
class TestWithRegexURLResolver(unittest.TestCase):
    """
    resolver test
    ~~~~~~~~~~~~
    Test the url re patterns via django.core.urlresolvers.RegexURLResolver
    """
    def setUp(self):
        self.module_name = "pylucid_project.apps.pylucid.views"
        # must be set, before the test starts:
        self.func_name = None

    def _resolve(self, path):
        urlconf = settings.ROOT_URLCONF
        resolver=RegexURLResolver(r'^/', urlconf)
        view_function, func_args, func_kwargs = resolver.resolve(path)

        module_name = view_function.__module__
        func_name = view_function.func_name
        return module_name, func_name, func_args, func_kwargs


    def path_test(self, path, args=(), kwargs={}, test_kwargs=True):
        """
        get the function information via the RegexURLResolver.
        test if the given function is the right module and method.
        """
        module_name, func_name, func_args, func_kwargs = self._resolve(path)

        self.assertEqual(self.module_name, module_name)
        self.assertEqual(self.func_name, func_name)
        self.assertEqual(args, func_args)
        if test_kwargs or func_kwargs:
            self.assertEqual(kwargs, func_kwargs)

    def test_root_page(self):
        self.func_name = "root_page"
        self.path_test("/")
        
    def test_resolve_url(self):
        self.func_name = "resolve_url"
        self.path_test("/de/slug/", kwargs={'lang_code': 'de', 'url_path': 'slug'})
        self.path_test("/de-at/slug/", kwargs={'lang_code': 'de-at', 'url_path': 'slug'})
        self.path_test("/de_at/slug/", kwargs={'lang_code': 'de_at', 'url_path': 'slug'})
        self.path_test("/de-AT/slug/", kwargs={'lang_code': 'de-AT', 'url_path': 'slug'})
        
    def test_existing_lang(self):
        self.func_name = "existing_lang"
        self.path_test("/slug1/slug2/", kwargs={'url_path': 'slug1/slug2'})
        self.path_test("/abc/de/", kwargs={'url_path': 'abc/de'})



if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', "pylucid.TestWithRegexURLResolver","pylucid.TestWithReverse")
