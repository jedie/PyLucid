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

try:
    from django.core.management import setup_environ, execute_from_command_line
except ImportError, err:
    _error("Can't import stuff from django", err)

try:
    import pylucid_project
except ImportError, err:
    _error("Can't import PyLucid", err)

try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError, err:
    _error("Can't import 'settings.py'", err)

try:
    # setup the environment before we start accessing things in the settings.
    setup_environ(settings_mod)
except Exception, err:
    _error("Can't setup the environment", err)

if __name__ == "__main__":
    try:
        execute_from_command_line()
    except Exception, err:
        _error("Error execute command", err)

