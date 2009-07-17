# coding: utf-8

"""
    PyLucid project unittest runner
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import errno
import unittest

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

import pylucid_project

#-----------------------------------------------------------------------------

PYLUCID_PROJECT_ROOT = os.path.abspath(os.path.dirname(pylucid_project.__file__))
UNITTEST_PLUGIN_SRC_PATH = os.path.join(PYLUCID_PROJECT_ROOT, "tests", "unittest_plugin")
UNITTEST_PLUGIN_DST_PATH = os.path.join(PYLUCID_PROJECT_ROOT, "pylucid_plugins", "unittest_plugin")

#-----------------------------------------------------------------------------

from django.conf import settings
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test.simple import run_tests

from pylucid_project.tests.test_tools import pylucid_test_data

from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS, PyLucidPlugin


TEST_NAMES = ["pylucid_project.tests", ]
for app_name in settings.INSTALLED_APPS:
    if app_name.startswith("pylucid"):
        TEST_NAMES.append("%s.tests" % app_name)

def setup_unittest_plugin(verbosity):
    """
    This must be done before the settings file would be imported, because in this
    moment all plugins will be scanned in the file system and "inserted" plugins after
    this, would be ignored. 
    """
    if not os.path.isdir(UNITTEST_PLUGIN_DST_PATH):
        if verbosity:
            print "insert unittest plugin via symlink ",
        try:
            os.symlink(UNITTEST_PLUGIN_SRC_PATH, UNITTEST_PLUGIN_DST_PATH)
        except OSError, err:
            if err.errno == errno.EEXIST:
                print "Error:", err
            else:
                raise
        if verbosity:
            print "OK"

    if verbosity:
        print "register unittest plugin",
    sys.path.insert(0, UNITTEST_PLUGIN_DST_PATH)

    unittest_plugin_instance = PyLucidPlugin(
        fs_path=UNITTEST_PLUGIN_DST_PATH, pkg_prefix="pylucid_project.pylucid_plugins",
        plugin_name="unittest_plugin"
    )
    PYLUCID_PLUGINS["unittest_plugin"] = unittest_plugin_instance
    PYLUCID_PLUGINS.init2()

    settings.INSTALLED_APPS += (unittest_plugin_instance.pkg_string,)
    settings.TEMPLATE_DIRS += (unittest_plugin_instance.get_template_path(),)
    if verbosity:
        print "OK"


def teardown_unittest_plugin(verbosity):
    if verbosity:
        print "remove unittest plugin symlink"
    os.remove(UNITTEST_PLUGIN_DST_PATH)


def _import_test(module_name, class_name=None):
    """
    Import test(s) from given module. Class_name is an array and may contain
    TestCase and test_method.
    """
    print module_name, class_name
    test_module = __import__(module_name, globals(), {}, [])
    if class_name:
        test_class = getattr(test_module, class_name[0], None)
        if len(class_name) == 1: # label is fname.TestClass
            try:
                return unittest.defaultTestLoader.loadTestsFromTestCase(test_class)
            except TypeError:
                raise ValueError("Test label '%s.%s' does not refer to a test class" %
                                 (module_name, '.'.join(class_name)))
        else: # label is fname.TestClass.test_method
            return test_class(class_name[1])
    else:
        try:
            return unittest.defaultTestLoader.loadTestsFromModule(test_module)
        except TypeError:
            raise TypeError("Test label '%s' wrong!" % module_name)


def get_all_tests(verbosity=False):
    """ Contruct a test suite from all available tests. Returns an instantiated test suite. """
    if verbosity:
        print "\nContruct a test suite from all available tests."
    if verbosity >= 2:
        print "Use test names: %r\n" % TEST_NAMES

    test_suite = unittest.TestSuite()

    for name in TEST_NAMES:
        try:
            tests = unittest.defaultTestLoader.loadTestsFromName(name)
        except AttributeError, err:
            if str(err) != "'module' object has no attribute 'tests'":
                # Skip only if no tests available
                raise
            if verbosity >= 2:
                print "Skip %r: %s" % (name, err)
        else:
            if verbosity:
                print "Add %s tests from %r" % (tests.countTestCases(), name)
            if verbosity >= 2:
                for testcase in tests:
                    for test in testcase._tests:
                        module_name = test.__class__.__module__
                        file_name = module_name.split(".")[-1]
                        print "\t%s.%s.%s" % (file_name, test.__class__.__name__, test._testMethodName)
            test_suite.addTest(tests)

    if verbosity:
        print

    return test_suite


def get_tests(test_labels, verbosity=False):
    """
    Construct a test suite with specified labels or all from all available
    tests if no labels are provided. Label should be of the form
    fname.TestClass or fname.TestClass.test_method. Returns an instantiated
    test suite corresponding to the label provided.
    """
    if verbosity:
        print "Building test suite."

    if test_labels:
        test_suite = unittest.TestSuite()
        for label in test_labels:
            parts = label.rsplit('.', 1)
            if len(parts) == 1:
                test_suite.addTest(_import_test(parts[0]))
            else:
                test_suite.addTest(_import_test(parts[0], parts[1:]))
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
    http://docs.djangoproject.com/en/dev/topics/testing/#defining-a-test-runner
    """
    if verbosity:
        print "start tests:", test_labels, "\n"

    setup_unittest_plugin(verbosity)

    setup_test_environment()

    old_name = settings.DATABASE_NAME

    from django.db import connection

    db_name = connection.creation.create_test_db(
        verbosity=verbosity, autoclobber=not interactive
    )
    if verbosity:
        print "\nTest database '%s' created" % db_name

    pylucid_test_data.create_pylucid_test_data(site=None, verbosity=verbosity)



    suite = get_tests(test_labels, verbosity)
    if verbosity:
        print "Running tests:"
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    connection.creation.destroy_test_db(old_name, verbosity)
    teardown_test_environment()

    teardown_unittest_plugin(verbosity)

    return len(result.failures) + len(result.errors)


if __name__ == "__main__":
    # Run all unitest directly
    from django.core import management
    management.call_command('test', verbosity=2)
