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
    from django.core.management import execute_from_command_line
except ImportError, err:
    _error("Can't import stuff from django", err)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pylucid_project.settings")
    try:
        execute_from_command_line(sys.argv)
    except Exception, err:
        _error("Error execute command", err)
    # except:
    #     import pdb, traceback
    #     print("-"*60)
    #     traceback.print_exc()
    #     print("-"*60)
    #     pdb.post_mortem()

