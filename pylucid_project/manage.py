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

def _error(msg, err):
    sys.stderr.write("%s: %s\n" % (msg, err))
    sys.stderr.write("-" * 79)
    sys.stderr.write("\n")
    import traceback
    traceback.print_exc()
    sys.stderr.write("-" * 79)
    sys.stderr.write("\n")
    sys.exit(1)

secret_key = "temp"

try:
    from django.core.management import execute_from_command_line
except ImportError as err:
    _error("Can't import stuff from django", err)

try:
    import pylucid_project
except ImportError as err:
    _error("Can't import PyLucid", err)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pylucid_project.management_command_settings")
# try:
#     from . import settings as settings_mod # Assumed to be in the same directory.
# except ImportError as err:
#     _error("Can't import 'settings.py'", err)

if __name__ == "__main__":
    try:
        execute_from_command_line(sys.argv)
    except Exception as err:
        _error("Error execute command", err)

