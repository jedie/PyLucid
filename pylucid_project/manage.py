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

def _error(msg):
    print "Import Error:", msg
    print "-" * 79
    import traceback
    traceback.print_exc()
    print "-" * 79
    print "Did you activate the virtualenv?"
    import sys
    sys.exit(1)

try:
    from django.core.management import setup_environ, execute_from_command_line
except ImportError, msg:
    _error(msg)


try:
    import pylucid_project
except ImportError, msg:
    _error(msg)
except:
    import traceback
    traceback.print_exc()


try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)
except:
    import traceback
    traceback.print_exc()

try:
    # setup the environment before we start accessing things in the settings.
    setup_environ(settings_mod)
except:
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    try:
        execute_from_command_line()
    except Exception:
        import traceback
        traceback.print_exc()

