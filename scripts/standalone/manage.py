#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid - manage.py
    ~~~~~~~~~~~~~~~~~~~


    http://docs.djangoproject.com/en/dev/ref/django-admin/

    borrowed from the pinax project.
"""

import os
import sys


os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

sys.stderr = sys.stdout


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
