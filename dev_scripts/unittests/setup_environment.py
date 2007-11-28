#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local test with a full init PyLucid environment
"""

import sys, os
from StringIO import StringIO

def setup_path(chdir, path_info):
    if path_info:
        print "os.getcwd() 1:", os.getcwd()
    if chdir == None:
        # Nothing to do (e.g. for local_dev_tests)
        return
    os.chdir(chdir) # go into PyLucid App root folder
    if path_info:
        print "os.getcwd() 2:", os.getcwd()
    sys.path.insert(0, os.getcwd())

def setup_django_environ():
    os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"
    from PyLucid import settings

    settings.DATABASE_ENGINE = "sqlite3"
    settings.DATABASE_NAME = ":memory:"

    print "- setup the django environ...",
    from django.core import management
    management.setup_environ(settings) # init django
    from django.test.utils import setup_test_environment
    setup_test_environment() # django global pre-test setup
    print "OK"

def make_syncdb():
    print "- create the model tables...",
    from django.core import management
    management.call_command('syncdb', verbosity=0, interactive=False)
    print "OK"

def make_insert_dump(extra_verbose):
    print "- insert the PyLucid install Dump...",
    if extra_verbose:
        print
    from PyLucid.install.install import DB_DumpFakeOptions
    from PyLucid.tools.db_dump import loaddb

    fake_options = DB_DumpFakeOptions()
    fake_options.verbose = extra_verbose

    if not extra_verbose:
        old_stderr = sys.stderr
        sys.stderr = StringIO()
    try:
        loaddb(app_labels = [], format = "py", options = fake_options)
    finally:
        if not extra_verbose:
            sys.stderr = old_stderr

    print "OK"

def install_internal_plugins(extra_verbose):
    print "- install internal plugins...",
#    if extra_verbose:
#        print

    from PyLucid.system import plugin_manager

    plugin_manager.install_internal_plugins(extra_verbose)
    print "OK"


def setup(chdir="../../pylucid", path_info=True, extra_verbose=True,
                        syncdb=True, insert_dump=True, install_plugins=False):
    """
    setup a test environment
    """
    print "Setup a local django environment for testing:"
    setup_path(chdir, path_info)
    setup_django_environ()
    if syncdb:
        make_syncdb()

    if insert_dump:
        make_insert_dump(extra_verbose)

    if install_plugins:
        install_internal_plugins(extra_verbose)

    print "-"*80
    print


#______________________________________________________________________________
# Fake PyLucid Environment

class FakePageMsg(object):
    def __call__(self, *msg):
        for line in msg:
            print line

class FakeUser(object):
    def is_anonymous(self):
        return True

class FakeRequest(object):
    user = FakeUser()
    META = {"HTTP_HOST": "unitest_HTTP_HOST_fake",}
    debug = True

class FakePage(object):
    id = 1

fakeURLs = {
    "absoluteIndex": "/",
}

#response = sys.stdout
def get_fake_context(page_object=None):
    if not page_object:
        from PyLucid.models import Page
        try:
            page_object = Page.objects.order_by('id')[1]
        except Exception:
            # Does only works, if the PyLucid dump inserted to the database
            page_object = FakePage()

    fake_context = {
        "request": FakeRequest(),
        "page_msg": FakePageMsg(),
        "URLs": fakeURLs,
        "PAGE": page_object,
        "CSS_ID_list": [],

    }

    return fake_context


#______________________________________________________________________________


if __name__ == "__main__":
    print "Local Test:"
    setup()

    print "-"*80
    from PyLucid.models import Page
    print "Existing pages:"
    for page in Page.objects.all():
        print " *", page

    print "END"