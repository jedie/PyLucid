#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid - manage.py
    ~~~~~~~~~~~~~~~~~~~
    
    http://docs.djangoproject.com/en/dev/ref/django-admin/
"""

from django.core.management import setup_environ, execute_from_command_line

import pylucid_project # only a test, if exist
from pylucid_project import settings as settings_mod

# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

if __name__ == "__main__":
    execute_from_command_line()

