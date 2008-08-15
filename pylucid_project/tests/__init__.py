#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unit tests
    ==================

    Testing PyLucid follows Django's testing framework. Preparation of test
    environment has following additions:
    - Test database is populated with PyLucid's default pages, templates
      and styles.
    - Internal plugins are installed.
    - Fully initialized database is dumped to a temporary file and that file is
      used as default fixture for test cases.

    Running tests
    -------------

    Unit tests can be run using django-admin.sh utility:

    > ./django-admin.sh test

    By default, this will run every test found in tests-subdirectory. If you
    only want to run tests from particular file under tests/-directory, add the
    application name to the command line. For example:

    > ./django-admin.sh test sha1_js_login

    You can be even more specific and add name of the test case and even method
    to the command line:

    > ./django-admin.sh test sha1_js_login.TestUserModels

    > ./django-admin.sh test sha1_js_login.TestUserModels.test_normal_test_user


    Writing tests
    -------------

    PyLucid unit tests are stored in pylucid/tests/-directory. During the test
    setup procedure that directory is scanned for .py-files, and test suites
    are tried to be loaded from them. Note: Subdirectories are not included in
    search of unit test.

    Pylucid.tests module provides custom TestCase class which provides some
    additional functions over django.test.TestCase and specifies test data
    fixture created during initialization of test environment. Thus
    pylucid.tests.TestCase is the preferred class to subclass for new unit
    tests which require access to PyLucid database. However, it has one
    drawback compared to unittest.TestCase, it is slower to execute. This is due
    to fact that at the start of each test case, before setUp() is run, Django
    will flush the database, and then the fixtures containing PyLucid initial
    data are loaded. This flush/load procedure is repeated for each test in the
    test case, so you can be certain that the outcome of a test will not be
    affected by another test, or by the order of test execution. Thus, if your
    test case does not need access PyLucid database, using standard
    unittest.TestCase as a parent class for test case will lead to faster test
    execution.

    The test database
    -----------------

    Tests that require a database (test cases inherited from tests.TestCase)
    will not use your “real” (production) database. A separate, blank database
    is created for the tests. This is by Django test framework see:
    [Django documentation](http://www.djangoproject.com/documentation/testing/#test-database)
    for details.

    Regardless of whether the tests pass or fail, the test database is
    destroyed when all the tests have been executed.

    Further reading
    ---------------
    [Django documentation](http://www.djangoproject.com/documentation/testing/)
    [Python unittest -- Unit testing framework](http://docs.python.org/lib/module-unittest.html)

    A place for improvement
    -----------------------
    Current test system does not support doctests.


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os
import re
import sys
import pprint
import shutil
import tempfile
import unittest
from StringIO import StringIO

os.environ['DJANGO_SETTINGS_MODULE'] = "PyLucid.settings"

from django.test.utils import setup_test_environment, teardown_test_environment
from django.test.utils import create_test_db, destroy_test_db

from django.conf import settings

from django.core.cache import cache
from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User, UNUSABLE_PASSWORD

from tests.utils.BrowserDebug import debug_response
from tests.utils.FakeRequest import FakePageMsg

from PyLucid.tools.db_dump import loaddb
from PyLucid.tools.Diff import make_diff, diff_lines
from PyLucid.install.install import DB_DumpFakeOptions
from PyLucid.models import Page, Style, Template, Plugin
from PyLucid.system.plugin_manager import auto_install_plugins, install_plugin


# Display invalid (e.g. misspelled, unused) template variables
# http://www.djangoproject.com/documentation/templates_python/#how-invalid-variables-are-handled
# http://www.djangoproject.com/documentation/settings/#template-string-if-invalid
settings.TEMPLATE_STRING_IF_INVALID = "XXX INVALID TEMPLATE STRING '%s' XXX"

TEST_USERS = {
    "superuser": {
        "username": "superuser",
        "email": "superuser@example.org",
        "password": "superuser_password",
        "is_staff": True,
        "is_superuser": True,
    },
    "staff": {
        "username": "staff test user",
        "email": "staff_test_user@example.org",
        "password": "staff_test_user_password",
        "is_staff": True,
        "is_superuser": False,
    },
    "normal": {
        "username": "normal test user",
        "email": "normal_test_user@example.org",
        "password": "normal_test_user_password",
        "is_staff": False,
        "is_superuser": False,
    },
}
# A User with a unusable password
TEST_UNUSABLE_USER = {
    "username": "unusable test user",
    "email": "unusable_test_user@example.org",
}


# A example page tree for some tests:
TEST_PAGES = [{
    'name': '1_AAA',
    'subitems': [
        {'name': '1_1_BBB'},
        {'name': '1_2_BBB',
            'subitems': [
                {'name': '1_2_1_CCC'},
                {'name': '1_2_2_CCC'}
            ]
        }
    ]
}, {
    'name': '2_DDD',
    'subitems': [
        {'name': '2_1_EEE'},
        {'name': '2_2_EEE'}
    ]
}]

# A list of shortcuts (from the example page tree)
TEST_PAGES_SHORTCUTS = [
    u'/1_AAA/',
    u'/1_AAA/1_1_BBB/',
    u'/1_AAA/1_2_BBB/',
    u'/1_AAA/1_2_BBB/1_2_1_CCC/',
    u'/1_AAA/1_2_BBB/1_2_2_CCC/',
    u'/2_DDD/',
    u'/2_DDD/2_1_EEE/',
    u'/2_DDD/2_2_EEE/'
]

# Temporary file for storing database fixture
FIXTURE_FILE = tempfile.NamedTemporaryFile(prefix='PyLucid_',suffix='.json')

# unittest plugin paths
# (relative path here! Because the current work dir can chaned!)
TEST_PLUGIN_SRC = "tests/unittest_plugin/"
TEST_PLUGIN_DST = "PyLucid/plugins_internal/unittest_plugin"


def change_preferences(plugin_name, **kwargs):
    """
    Change plugin preferences
    """
    # Get plugin+preferences
    plugin = Plugin.objects.get(plugin_name = plugin_name)
    preferences = plugin.default_pref.get_data()
    preferences.update(kwargs)

    # Check the new preferences via newforms from the plugin config file
    unbound_form = plugin.get_pref_form(page_msg=FakePageMsg(), verbosity=1)

    form = unbound_form(preferences)
    assert form.is_valid(), "Error change preferences: %s" % repr(form.errors)

    # Save the new preferences
    plugin.default_pref.set_data(preferences, user=None)
    plugin.default_pref.save()


def _check_cachebackend():
    """
    Test if in settings is a cache backend setup and if it works.
    Some tests depends on the cache backend, see:
    http://pylucid.net:8080/pylucid/ticket/203
    """
    def error():
        error_msg = (
            "Cache test.\n"
            "Cache backend test failed.\n"
            "The cache unittest needs a working cache backend!\n"
            "Please setup CACHE_BACKEND in your settings.py\n"
            "Note: All cache tests will be skipped!"
            )
        print error_msg
        return False

    cache_key = "unitest cache key"
    content = "A simple test content..."

    cache.set(cache_key, content, 10)
    test = cache.get(cache_key)
    if test != content:
        return error()

    cache.delete(cache_key)
    test = cache.get(cache_key)
    if test != None:
        return error()

    # cache backend works
    return True

WORKING_CACHE_BACKEND = _check_cachebackend()

def requires_cache(test):
    """ Decorator for tests that require working cache backend.

    Whole TestCache class is meaningless with out working cache, but Python 2.4
    does not support decoration of classes."""
    if WORKING_CACHE_BACKEND:
        return test
    else:
        def dummy(*args):
            pass
        return dummy


class TestCase(DjangoTestCase):
    """
    PyLucid test case.
    """
    fixtures = [FIXTURE_FILE.name]

    # A simple regex to get all html links out of a page content
    HREF_RE = re.compile('<a href="(.+?)".*?>(.+?)</a>')

    def assertResponse(self, response, must_contain=(), must_not_contain=()):
        """
        Check the content of the response
        must_contain - a list with string how must be exists in the response.
        must_not_contain - a list of string how should not exists.
        """
        def error(respose, msg):
            debug_response(
                response, self.one_browser_traceback, msg, display_tb=False
            )
            raise self.failureException, msg

        for txt in must_contain:
            if not txt in response.content:
                error(response, "Text not in response: '%s'" % txt)

        for txt in must_not_contain:
            if txt in response.content:
                error(response, "Text should not be in response: '%s'" % txt)

    def assertEqual2(self, first, second, error_msg=None):
        """
        Same as the original, but display a diff on error.
        Makes only sence if the string contains more lines (\n)
        """
        if first == second:
            # is equal, ok
            return

        if error_msg:
            error_msg += "\n"
        else:
            error_msg = ""

        error_msg += "Strings not equal:\n"
        error_msg += "1: %r\n" % first
        error_msg += "2: %r\n" % second
        error_msg += "Diff:\n"
        error_msg += diff_lines(first, second)

        self.fail(error_msg)

    def assertLists(self, is_list, should_be_list, sort=True):
        """
        Compares two lists how should be the same.
        If the lists has different content, is display a diff and raised a
        AssertionError.
        """
        if sort:
            is_list.sort()
            should_be_list.sort()

        error_msg = ""

        if is_list != should_be_list:
            is_list2 = pprint.pformat(is_list)
            should_be_list2 = pprint.pformat(should_be_list)
            error_msg += "The two lists are not the same:\n"
            for line in make_diff(should_be_list2, is_list2):
                error_msg += "%s\n" % line

        self.assertEqual(
            is_list, should_be_list, error_msg
        )

    #__________________________________________________________________________
    # Special assert methods for plugin access:
    def assertPluginAccess(self, base_url, plugin_name, method_names,
                                        must_contain=(), must_not_contain=()):
        """
        Shared method. Checks all given method.
        base_url is e.g.: "/%s/1" % settings.COMMAND_URL_PREFIX
        """
        for method_name in method_names:
            url = "/".join([base_url, plugin_name, method_name, ""])
            response = self.client.get(url)
            self.failUnlessEqual(response.status_code, 200)
            self.assertResponse(
                response, must_contain, must_not_contain
            )

    def assertAccessDenied(self, base_url, plugin_name, method_names):
        """
        Test a list of plugin methods, how *aren't* accessable for the current
        user.
        """
        self.assertPluginAccess(
            base_url, plugin_name, method_names,
            must_contain=("[Permission Denied!]",),
            must_not_contain=("Traceback",)
        )

    def assertAccessAllowed(self, base_url, plugin_name, method_names):
        """
        Test a list of plugin methods, how *are* accessable for the current
        user.
        """
        self.assertPluginAccess(
            base_url, plugin_name, method_names,
            must_not_contain=("AccessDenied", "Error", "Traceback")
        )

    # _________________________________________________________________________

    def assertPyLucid404(self, url):
        """
        Check if the given url raised a PyLucid own 404 page.
        """
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 404)
        self.assertResponse(
            response,
            must_contain=("404", "Page not found", "back to",),
            must_not_contain=("DEBUG = True",)
        )

    def assertDjango404(self, url):
        """
        Check if the given url raise the django 404 debug page.
        """
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 404)
        self.assertResponse(
            response,
            must_contain=("(404)", "Page not found", "DEBUG = True",),
            must_not_contain=("Traceback", "back to")
        )

    # _________________________________________________________________________
    def login(self, usertype):
        """
        Login the user defined in TEST_USERS
        """
        ok = self.client.login(username=TEST_USERS[usertype]["username"],
                               password=TEST_USERS[usertype]["password"])
        self.failUnless(ok, "Can't login test user '%s'!" % usertype)

    # _________________________________________________________________________
    # methods to get information and test the content:
    def get_links(self, content):
        """
        Return all links found with the HREF_RE.
        """
        return self.HREF_RE.findall(content)

    # _________________________________________________________________________
    # link snapshot:

    def _snapshot_iter(self):
        """
        shared method for create_link_snapshot() and link_snapshot_test()
        """
        for page in Page.objects.all().order_by("position", "name", "id"):
            url = page.get_absolute_url()

            response = self.client.get(url)
            self.failUnlessEqual(response.status_code, 200)

            content = response.content.strip()
            links = self.get_links(content)
            yield (url, links)

    def link_snapshot_test(self, snapshot):
        """
        Compare a reference snapshot with the real links.
        """
        is_links = []
        should_be_links = []
        for url, links in self._snapshot_iter():
            is_links.append(links)
            should_be_links.append(snapshot[url])

        #print "is_links:", is_links
        #print "should_be_links:", should_be_links
        self.assertLists(is_links, should_be_links, sort=False)

    def create_link_snapshot(self, print_result=True):
        """
        Build a a reference snapshot for a unittest.
        Display it via pprint and returned it, too.
        Usefull for copy&paste the output into this source file :)
        """
        if print_result:
            print "Build a snapshot for the unittest compare:"
            print "-"*79

        data = {}
        for url, links in self._snapshot_iter():
            data[url] = links

        if print_result:
            result = pprint.pformat(data)
            lines = result.splitlines()
            print "        snapshot = %s" % lines[0]
            for line in lines[1:]:
                print "            %s" % line
            print "-"*79
        return data


def load_db_dumps(extra_verbosity):
    """
    Insert PyLucid default pages to test database.
    """
    print "Loading PyLucid database dump ",
    if extra_verbosity:
        print
    fake_options = DB_DumpFakeOptions()
    fake_options.verbose = extra_verbosity
    if not extra_verbosity:
        old_stderr = sys.stderr
        sys.stderr = StringIO()
    try:
        loaddb(app_labels = [], format = "py", options = fake_options)
    finally:
        if not extra_verbosity:
            sys.stderr = old_stderr
    print ""

def install_internal_plugins(verbosity):
    """
    Install PyLucid Internal plugins
    """
    print "Installing PyLucid internal plugins ",
    auto_install_plugins(
        debug=True, page_msg=FakePageMsg(), verbosity=verbosity
    )
    print ""



def init_unittest_plugin():
    """
    initialize the unittest plugin
    -copy ./tests/unittest_plugin/ into ./PyLucid/plugins_internal/

    The plugin would be installed in install_internal_plugins() as a normal Plugin.
    """
    print "initialize the unittest plugin"
    if os.path.exists(TEST_PLUGIN_DST):
        print "Info: old unitest plugin exist."
        remove_unittest_plugin()

    print "copy %s to %s" % (TEST_PLUGIN_SRC, TEST_PLUGIN_DST)
    try:
        shutil.copytree(
            os.path.abspath(TEST_PLUGIN_SRC), os.path.abspath(TEST_PLUGIN_DST)
        )
    except OSError, err:
        import errno
        if err.errno == errno.EEXIST: # [Errno 17] File exists
            # A prior unittest run aborted?
            print "Info:", err
        else:
            print "os.getcwd():", os.getcwd()
            raise



def remove_unittest_plugin():
    print "remove unittest plugin (%s)" % TEST_PLUGIN_DST
    shutil.rmtree(os.path.abspath(TEST_PLUGIN_DST))


def create_user(username, password, email, is_staff, is_superuser):
    """
    Create a user and return the instance.
    """
    defaults = {'password':password, 'email':email}
    user, created = User.objects.get_or_create(
        username=username, defaults=defaults
    )
    if not created:
        user.email = email
    user.set_password(password)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save()
    return user

def create_users():
    """
    Create all available testusers.
    """
    # Create all users with a usable password
    for usertype, userdata in TEST_USERS.iteritems():
        create_user(**userdata)

    # Create the user with a unusable password
    user = User.objects.create_user(**TEST_UNUSABLE_USER)
    user.set_unusable_password()
    user.save()


def create_template(**kwargs):
    """
    Delete all existing templates, create a new one and return the instance.
    """
    Template.objects.all().delete()

    template = Template(**kwargs)
    template.save()
    return template

def create_stylesheet(**kwargs):
    """
    Delete all existing styles, create a new one and return the instance.
    """
    Style.objects.all().delete()

    style = Style(**kwargs)
    style.save()
    return style


def create_page(**kwargs):
    """
    Creates Page object with given kwargs.
    """
    default_user = User.objects.get(
        username=TEST_USERS["superuser"]["username"]
    )
    default_template = Template.objects.all()[0]
    default_style = Style.objects.all()[0]
    default_markup = 0 # html without TinyMCE

    page = Page(
        name             = kwargs.get("name", "New Page"),
        shortcut         = kwargs.get("shortcut", None),
        content          = kwargs.get("content", "TestPageContent"),
        template         = kwargs.get("template", default_template),
        style            = kwargs.get("style", default_style),
        markup           = kwargs.get("markup", default_markup),
        createby         = kwargs.get("user", default_user),
        lastupdateby     = kwargs.get("user", default_user),
        showlinks        = kwargs.get("showlinks", True),
        permitViewPublic = kwargs.get("permitViewPublic", True),
        permitViewGroup  = kwargs.get("permitViewGroup", None),
        permitEditGroup  = kwargs.get("permitEditGroup", None),
        parent           = kwargs.get("parent", None),
        )
    page.save()
    return page

def create_pages(data, parent = None, **kwargs):
    """
    Create pages recursively.
    """
    for page_data in data:
        page_data = page_data.copy()
        page_data.update(kwargs)
        page_data["parent"] = parent
        last_page = create_page(**page_data)
        if "subitems" in page_data:
            create_pages(
                page_data["subitems"], last_page, **kwargs
                )

def create_test_fixture(verbosity,format='json'):
    from django.core.management.commands import dumpdata
    data = dumpdata.Command().handle(format=format,traceback=True)
    FIXTURE_FILE.write(data)
    FIXTURE_FILE.flush()

def init_pyluciddb(verbosity):
    """
    Initilize PyLucid database, loads database dumps, installs basic plugins
    and ensures that at least testuser exists.
    """
    load_db_dumps(verbosity)
    init_unittest_plugin()
    install_internal_plugins(verbosity)
    create_users() # Create all test users
    create_pages(TEST_PAGES) # Create the test pages
    create_test_fixture(verbosity)


def teardown_pylucid():
    """
    cleanup
    """
    remove_unittest_plugin()

def _import_test(module_name, class_name=None):
    """
    Import test(s) from given module. Class_name is an array and may contain
    TestCase and test_method.
    """
    test_module = __import__(module_name, globals(), {}, [])
    if class_name:
        test_class = getattr(test_module, class_name[0], None)
        if len(class_name) == 1: # label is fname.TestClass
            try:
                return unittest.defaultTestLoader.loadTestsFromTestCase(test_class)
            except TypeError:
                raise ValueError("Test label '%s.%s' does not refer to a test class" %
                                 (module_name,'.'.join(class_name)))
        else: # label is fname.TestClass.test_method
            return test_class(class_name[1])
    else:
        try:
            return unittest.defaultTestLoader.loadTestsFromModule(test_module)
        except TypeError:
            raise TypeError("Test label '%s' wrong!" % module_name)

def get_all_tests(verbosity=False):
    """
    Contruct a test suite from all available tests. Inspects all .py-files in the
    package directory, and tries to load test suites from them. Does not go
    into subdirectories. Returns an instantiated test suite.
    """
    print "Contruct a test suite from all available tests."
    test_suite = unittest.TestSuite()
    for dir_item in os.listdir(__path__[0]):
        full_path = os.path.join(__path__[0], dir_item)
        if full_path == __file__:
            # Skip this file
            continue
        if os.path.isdir(full_path):
            # Skip directories
            if verbosity:
                print "Skipping directory %s." % dir_item
                continue
        if dir_item.endswith('.py'):
            if verbosity:
                print "Inspecting %s" % dir_item
            test_suite.addTests(_import_test(dir_item[:-3]))
    return test_suite

def get_tests(test_labels, verbosity=False):
    """
    Construct a test suite with specified labels or all from all available
    tests if no labels are provided. Label should be of the form
    fname.TestClass or fname.TestClass.test_method. Returns an instantiated
    test suite corresponding to the label provided.
    """
    print "Building test suite."
    if test_labels:
        test_suite = unittest.TestSuite()
        for label in test_labels:
            parts = label.split('.')
            if len(parts) == 1:
                test_suite.addTest(_import_test(parts[0]))
            else:
                test_suite.addTest(_import_test(parts[0],parts[1:]))
        return test_suite
    else:
        return get_all_tests(verbosity)

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """
    PyLucid test runner. Sets up test environment, populates test database with
    initial data, gathers unittest test suite, runs tests, reports results and
    finally removes test database and cleans up environment.

    Run the unit tests for all the test labels in the provided list.
    Labels must be of the form:
     - fname.TestClass.test_method
        Run a single specific test method
     - fname.TestClass
        Run all the test methods in a given class
     - fname
        Search for doctests and unittests in the named application.
    where fname is the name of the file containing tests in 'tests'-directory,
    without extension.

    See:
    http://www.djangoproject.com/documentation/testing/#defining-a-test-runner
    """
    print "test start."
    settings.DEBUG = False
    setup_test_environment()
    old_name = settings.DATABASE_NAME
    db_name = create_test_db(verbosity=1, autoclobber=not interactive)
    init_pyluciddb(verbosity==2)
    suite = get_tests(test_labels, verbosity==2)
    print "Running tests"
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    destroy_test_db(old_name, verbosity)
    teardown_test_environment()
    teardown_pylucid()

    return len(result.failures) + len(result.errors)


print "PyLucid unittest"
