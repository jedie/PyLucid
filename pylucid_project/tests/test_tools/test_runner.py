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

from django.conf import settings
from django.test.testcases import TestCase
from django.db.models.loading import get_app, get_apps
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test.simple import DjangoTestSuiteRunner, build_test, build_suite, reorder_suite

import pylucid_project
from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS, PyLucidPlugin

#-----------------------------------------------------------------------------

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

    def print_verbose_info(self, tests, test_name):
        if self.verbosity:
            print "Add %s tests from %r" % (tests.countTestCases(), test_name)
        if self.verbosity >= 2:
            for testcase in tests:
                for test in testcase._tests:
                    module_name = test.__class__.__module__
                    file_name = module_name.split(".")[-1]
                    print "\t%s.%s.%s" % (file_name, test.__class__.__name__, test._testMethodName)

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
                        print "Skip %r: %s" % (test_name, err)
                else:
                    self.print_verbose_info(tests, test_name)
                    test_suite.addTest(tests)

        return test_suite



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
    management.call_command('test', verbosity=2)
