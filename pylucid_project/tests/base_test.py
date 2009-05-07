
import unittest

import test_tools

from django.test.client import Client

#import django_tools


class BaseTest(unittest.TestCase):
    def test(self):
        c = Client()
        response = c.get('/admin/')
        print response.content



if __name__ == "__main__":
    # Run this unitest directly
    import os
    filename = os.path.splitext(os.path.basename(__file__))[0]
    test_tools.test_runner.run_tests(test_labels=[filename])