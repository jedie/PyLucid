# coding: utf-8

"""
    PyLucid project unittest runner
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import pprint
import sys
import unittest


if __name__ == "__main__":
    # Run all unittest directly
    from pylucid_project.tests import run_test_directly
    run_test_directly(
        verbosity=2,
#        failfast=True,
        failfast=False,
    )
    sys.exit()


from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

import pylucid_project
from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS, PyLucidPlugin

#-----------------------------------------------------------------------------

# Disable dynamic site, if used:
if getattr(settings, "USE_DYNAMIC_SITE_MIDDLEWARE", False):
    settings.USE_DYNAMIC_SITE_MIDDLEWARE = False
    settings.SITE_ID = 1

PYLUCID_PROJECT_ROOT = os.path.abspath(os.path.dirname(pylucid_project.__file__))
UNITTEST_PLUGIN_SRC_PATH = os.path.join(PYLUCID_PROJECT_ROOT, "tests", "unittest_plugin")
UNITTEST_PLUGIN_DST_PATH = os.path.join(PYLUCID_PROJECT_ROOT, "pylucid_plugins", "unittest_plugin")

#-----------------------------------------------------------------------------


class PyLucidTestRunner(DjangoTestSuiteRunner):
    def _get_all_test_names(self):
        """  """
        test_names = ["pylucid_project.tests", ]
        for app_name in settings.INSTALLED_APPS:
            test_names.append("%s.tests" % app_name)

    def is_in_test_labels(self, app_name, test_labels):
        for test_label in test_labels:
            if test_label in app_name:
                return True
        return False

    def print_test_names(self, tests):
        if hasattr(tests, "_tests"):
            for test in tests:
                self.print_test_names(test)
        else:
            module_name = tests.__class__.__module__
            file_name = module_name.split(".")[-1]
            print "\t%s.%s.%s" % (file_name, tests.__class__.__name__, tests._testMethodName)

    def print_verbose_info(self, tests, test_name):
        if self.verbosity:
            print "Add %s tests from %r" % (tests.countTestCases(), test_name)
        if self.verbosity >= 2:
            self.print_test_names(tests)

    def _setup_unittest_plugin(self):
        if os.path.exists(UNITTEST_PLUGIN_DST_PATH):
            print "unitest plugin already exist in: %r" % UNITTEST_PLUGIN_DST_PATH
        else:
            print "insert unittest plugin via symlink:"
            print "%s -> %s" % (UNITTEST_PLUGIN_SRC_PATH, UNITTEST_PLUGIN_DST_PATH)
            os.symlink(UNITTEST_PLUGIN_SRC_PATH, UNITTEST_PLUGIN_DST_PATH)

        template_dir = os.path.join(UNITTEST_PLUGIN_DST_PATH, "templates")
        if not template_dir in settings.TEMPLATE_DIRS:
            print "unittest_plugin added to settings.TEMPLATE_DIRS"
            settings.TEMPLATE_DIRS += (template_dir,)

        plugin_name = "pylucid_project.pylucid_plugins.unittest_plugin"
        if not plugin_name in settings.INSTALLED_APPS:
            print "unittest_plugin added to settings.INSTALLED_APPS"
            settings.INSTALLED_APPS += (plugin_name,)

        if not "unittest_plugin" in PYLUCID_PLUGINS:
            pkg_path = os.path.join(PYLUCID_PROJECT_ROOT, "pylucid_plugins")
            PYLUCID_PLUGINS["unittest_plugin"] = PyLucidPlugin(
                pkg_path, section="pylucid_project",
                pkg_dir="pylucid_plugins", plugin_name="unittest_plugin"
            )
            print "unittest_plugin added to PYLUCID_PLUGINS"
            print PYLUCID_PLUGINS.keys()

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        """
        Contruct a test suite from all available tests. Returns an instantiated test suite.
        
        The django test suite runner used django.db.models.loading.get_app() to get all tests.
        The problem is get_app() is a list of all apps witch have a models.py
        
        We want run tests from pylucid plugin witch have no models.py, too.
        
        test_labels can contain the absolute path to a app. This is needful,
        because we can add this into a test file:
            management.call_command('test', __file__)
        """
        test_suite = unittest.TestSuite()

        if test_labels:
            # add only test labels
            for test_label in test_labels:
                if "pylucid" not in test_label:
                    print "Skip test label %r: it's not a pylucid part!" % test_label
                    print " Use default settings.TEST_RUNNER to run this test!"
                    continue

                if os.path.isfile(test_label):
                    # run test directly and use __file__ to insert the current test label
                    raw_test_label = os.path.splitext(test_label)[0]
                    test_dir_splitted = raw_test_label.rsplit(os.sep, 3)
                    test_label = ".".join(test_dir_splitted[1:4])
                    if self.verbosity:
                        print "cut __file__ path to %r" % test_label

                try:
                    tests = unittest.defaultTestLoader.loadTestsFromName(test_label)
                except Exception, err:
                    etype, evalue, etb = sys.exc_info()
                    evalue = etype("Can't get test label %r: %s" % (test_label, evalue))
                    raise etype, evalue, etb

                self.print_verbose_info(tests, test_label)
                test_suite.addTest(tests)
        else:
            # Add all pylucid related apps
            if self.verbosity >= 2:
                print "INSTALLED_APPS:"
                pprint.pprint(settings.INSTALLED_APPS)
            for app_name in settings.INSTALLED_APPS:
                if "pylucid" not in app_name:
                    # use only PyLucid stuff
                    continue

                test_name = "%s.tests" % app_name

                try:
                    tests = unittest.defaultTestLoader.loadTestsFromName(test_name)
                except AttributeError, err:
                    if str(err) != "'module' object has no attribute 'tests'":
                        # Other error than "no tests available"
                        raise
                    if self.verbosity >= 2:
                        print "Skip %r, ok. (%s)" % (test_name, err)
                except Exception, err:
                    print "*** Error in %r: %s" % (test_name, err)
                else:
                    self.print_verbose_info(tests, test_name)
                    test_suite.addTest(tests)

        return test_suite

    def setup_test_environment(self, *args, **kwargs):
        self._setup_unittest_plugin()
        super(PyLucidTestRunner, self).setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        print "remove unittest plugin symlink"
        os.remove(UNITTEST_PLUGIN_DST_PATH)
        super(PyLucidTestRunner, self).teardown_test_environment(*args, **kwargs)

