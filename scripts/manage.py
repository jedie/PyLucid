#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid - manage.py
    ~~~~~~~~~~~~~~~~~~~


    Please change ROOT_DIR path to your needs!


    http://docs.djangoproject.com/en/dev/ref/django-admin/

    borrowed from the pinax project.
"""

import os
import sys


##############################################################################
# Change this path:
ROOT_DIR = "/update/path/to/PyLucid_env/"
##############################################################################


os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

sys.path.insert(0, os.path.join(ROOT_DIR, "src/pylucid/pylucid_project"))

sys.stderr = sys.stdout

print "virtualenv activate...",
virtualenv_file = os.path.join(ROOT_DIR, "bin/activate_this.py")
try:
    execfile(virtualenv_file, dict(__file__=virtualenv_file))
except Exception, err:
    print "Error: Can't activate the virtualenv!"
    print
    print "Failed to execute file %r" % virtualenv_file
    print
    print "-" * 79
    import traceback
    traceback.print_exc()
    print "-" * 79
    print
    print "ROOT_DIR = %r" % ROOT_DIR
    print "Please check ROOT_DIR in this file (%s)" % __file__
    print
    sys.exit(1)

print "OK"






def _error(msg):
    print "Import Error:", msg
    print "-" * 79
    import traceback
    traceback.print_exc()
    print "-" * 79
    print "Did you activate the virtualenv?"
    sys.exit(1)

try:
    from django.core.management import setup_environ, execute_from_command_line
except ImportError, msg:
    _error(msg)


try:
    import pylucid_project
except ImportError, msg:
    _error(msg)


try:
    import settings as settings_mod
except ImportError:
    sys.stderr.write("Error: Can't import settings.py\n")
    sys.exit(1)


# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

if __name__ == "__main__":
    execute_from_command_line()
