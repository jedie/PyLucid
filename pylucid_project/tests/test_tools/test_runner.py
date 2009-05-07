
import os
import unittest

from django.conf import settings
from django.test.utils import setup_test_environment, teardown_test_environment


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
    setup_test_environment()
    old_name = settings.DATABASE_NAME
    
    from django.db import connection
    
    db_name = connection.creation.create_test_db(
        verbosity=1, autoclobber=not interactive
    )
    print "Test database '%s' created" % db_name  
#    init_pyluciddb(verbosity==2)
    suite = get_tests(test_labels, verbosity==2)
    print "Running tests"
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    connection.creation.destroy_test_db(old_name, verbosity)
    teardown_test_environment()
#    teardown_pylucid()

    return len(result.failures) + len(result.errors)
