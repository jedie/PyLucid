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

import tests # setup the environment

from django.conf import settings

# Switch settings for local test, see DocString above.
#settings.ENABLE_INSTALL_SECTION = True
#settings.ENABLE_INSTALL_SECTION = False
#settings.SERVE_STATIC_FILES = True
#settings.SERVE_STATIC_FILES = False

from django.core.urlresolvers import reverse, RegexURLResolver, NoReverseMatch

# print "Used url patterns:"
# print "-"*80
# from PyLucid.urls import urls
# for url in urls:
#     print url
# print "-"*80


class TestURLpatterns_reverse_test(unittest.TestCase):
    """
    reverse test
    ~~~~~~~~~~~~
    Test the url re patterns via django.core.urlresolvers.reverse
    """
    def test_reverse_install_view(self):
        """
        url to a _install view
        """
        view = 'PyLucid.install.index.menu'
        
        if settings.ENABLE_INSTALL_SECTION == True:
            # The _install section is activated
            self.assertEqual(reverse(view), "/_install")
        else:
            # _install section deactivaed
            self.failUnlessRaises(NoReverseMatch, reverse, view)        

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
            reverse('PyLucid.index.index', args=[""]), "/"
        )
        self.assertEqual(
            reverse('PyLucid.index.index', args=["shortcut"]), "/shortcut"
        )
        self.assertEqual(
            reverse('PyLucid.index.index', args=["1/2"]), "/1/2"
        )


class TestURLpatterns(unittest.TestCase):
    """
    resolver test
    ~~~~~~~~~~~~
    Test the url re patterns via django.core.urlresolvers.RegexURLResolver
    """
    def setUp(self):
        # must be set, before the test starts
        self.module_name = None
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
        if test_kwargs:
            self.assertEqual(kwargs, func_kwargs)


    def test_install_section(self):
        """
        Test the _install section
        """      
        path = "/%s" % settings.INSTALL_URL_PREFIX
        module_name, func_name, func_args, func_kwargs = self._resolve(path)
        
        if settings.ENABLE_INSTALL_SECTION == False:
            # Must no be go to the normal CMS view
            self.assertEqual(module_name, 'PyLucid.index')
            self.assertEqual(func_name, 'index')
        else:
            # _install section enabled -> Display _install menu
            self.assertEqual(module_name, "PyLucid.install.index")
            self.assertEqual(func_name, 'menu')       

    def test_cms_view(self):
        """
        url for normal cms views
        """
        self.module_name = "PyLucid.index"
        self.func_name = "index"

        self.path_test("/", args=("",))
        self.path_test(
            "/shortcut1/",
            args=('shortcut1/',)
        )
        self.path_test(
            "/shortcut1/shortcut2/",
            args=('shortcut1/shortcut2/',)
        )
        self.path_test(
            "/shortcut1/shortcut2/shortcut3/",
            args=('shortcut1/shortcut2/shortcut3/',)
        )

    def test_permalink(self):
        """
        url for normal cms views
        """
        base_path = "/%s" % settings.PERMALINK_URL_PREFIX
        self.module_name = "PyLucid.index"

        # wrong permalinks -> the index view answers
        self.func_name = "index"
        self.path_test(
            base_path,
            args=('_goto',)
        )
        self.path_test(
            base_path + "/wrong",
            args=('_goto/wrong',)
        )
        self.path_test(
            base_path + "/wrong/",
            args=('_goto/wrong/',)
        )
        self.path_test(
            base_path + "/1",
            args=('_goto/1',)
        )

        # right permalinks
        self.func_name = "permalink"
        self.path_test(base_path + "/1/", kwargs = {'page_id': '1'})
        self.path_test(base_path + "/1/shortcut", kwargs = {'page_id': '1'})
        self.path_test(base_path + "/1/shortcut/", kwargs = {'page_id': '1'})

    def test_command_url(self):
        """
        _command urls
        """
        base_path1 = "/%s" % settings.COMMAND_URL_PREFIX
        base_path2 = "/%s/1/module_name/method_name/" % \
                                                settings.COMMAND_URL_PREFIX
        self.module_name = "PyLucid.index"

        # wrong _command links -> the index view answers
        self.func_name = "index"
        self.path_test(
            base_path1,
            args=(settings.COMMAND_URL_PREFIX,)
        )
        self.path_test(
            base_path1 + "/",
            args=(settings.COMMAND_URL_PREFIX + "/",)
        )
        self.path_test(
            base_path1 + "/wrong",
            args=(settings.COMMAND_URL_PREFIX + "/wrong",)
        )
        self.path_test(
            base_path1 + "/wrong/",
            args=(settings.COMMAND_URL_PREFIX + "/wrong/",)
        )
        self.path_test(
            base_path1 + "/wrong/wrong_too",
            args=(settings.COMMAND_URL_PREFIX + "/wrong/wrong_too",)
        )
        self.path_test(
            base_path1 + "/wrong/wrong_too/",
            args=(settings.COMMAND_URL_PREFIX + "/wrong/wrong_too/",)
        )
        self.path_test(
            base_path1 + "/1",
            args=(settings.COMMAND_URL_PREFIX + "/1",)
        )
        self.path_test(
            base_path1 + "/1/",
            args=(settings.COMMAND_URL_PREFIX + "/1/",)
        )
        self.path_test(
            base_path1 + "/1/wrong",
            args=(settings.COMMAND_URL_PREFIX + "/1/wrong",)
        )
        self.path_test(
            base_path1 + "/1/wrong/",
            args=(settings.COMMAND_URL_PREFIX + "/1/wrong/",)
        )

        # right _command links
        self.func_name = "handle_command"
        self.path_test(
            base_path2,
            kwargs = {
                'method_name': 'method_name',
                'module_name': 'module_name',
                'page_id': '1',
                'url_args': ''
            }
        )
        self.path_test(
            base_path2 + "url_args",
            kwargs = {
                'method_name': 'method_name',
                'module_name': 'module_name',
                'page_id': '1',
                'url_args': 'url_args'
            }
        )
        self.path_test(
            base_path2 + "url_args1/url_args2",
            kwargs = {
                'method_name': 'method_name',
                'module_name': 'module_name',
                'page_id': '1',
                'url_args': 'url_args1/url_args2'
            }
        )
        self.path_test(
            base_path2 + "url_args1/url_args2/3/4",
            kwargs = {
                'method_name': 'method_name',
                'module_name': 'module_name',
                'page_id': '1',
                'url_args': 'url_args1/url_args2/3/4'
            }
        )

    def test_install_url(self):
        """
        the _install section urls
        """
        if settings.ENABLE_INSTALL_SECTION == False:
            print "Install section deactivaed, skip url tests"
            return
        
        base_path = "/%s" % settings.INSTALL_URL_PREFIX
        self.module_name = "PyLucid.install.index"

        self.func_name = "menu"
        self.path_test(base_path)
        self.path_test(base_path + "/")

        self.func_name = "logout"
        self.path_test(base_path + "/logout/")

        self.func_name = "run_method"
        self.path_test(
            base_path + "/module_name/method_name/",
            kwargs = {
                'method_name': 'method_name',
                'module_name': 'module_name',
                'url_args': ''
            }
        )
        self.path_test(
            base_path + "/module_name/method_name/arg1/",
            kwargs = {
                'method_name': 'method_name',
                'module_name': 'module_name',
                'url_args': 'arg1/'
            }
        )
        self.path_test(
            base_path + "/module_name/method_name/arg1/2",
            kwargs = {
                'method_name': 'method_name',
                'module_name': 'module_name',
                'url_args': 'arg1/2'
            }
        )

    def test_static_serve(self):
        """
        check the media urls
        """
        base_path = "/%s/" % settings.MEDIA_URL.strip("/")
        
        if settings.SERVE_STATIC_FILES == False:
            print "settings.SERVE_STATIC_FILES == False, skip tests"
            module_name, func_name, func_args, func_kwargs = \
                                                        self._resolve(base_path)
            # Must no be go to the normal CMS view
            self.assertEqual(module_name, 'PyLucid.index')
            self.assertEqual(func_name, 'index')
            return
        
        self.module_name = "django.views.static"
        self.func_name = "serve"

        self.path_test(base_path, test_kwargs=False)
        self.path_test(base_path + "path", test_kwargs=False)
        self.path_test(base_path + "path/", test_kwargs=False)
        self.path_test(base_path + "path1/path2", test_kwargs=False)
        self.path_test(base_path + "path1/path2/", test_kwargs=False)


if __name__ == "__main__":
    # Run this unitest directly
    import tests # FIXME: We don't need the database here
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])