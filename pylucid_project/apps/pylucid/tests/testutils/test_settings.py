# coding: utf-8

from pylucid_project.settings import *

#INSTALLED_APPS = (
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
#    'django.contrib.admin',
#
#    'pylucid',
#)

DATABASE_ENGINE = "sqlite3"
DATABASE_NAME = ":memory:"

SITE_ID = 1

ROOT_URLCONF = "pylucid.tests.testutils.test_urls"

TEST_RUNNER = 'django.test.simple.run_tests'