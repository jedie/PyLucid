#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    A small local django test.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sometimes I would like to test a codesnippet without a complete
    django environment. Here is a small "local test script" you can
    use for this ;)

    http://www.djangosnippets.org/snippets/252/
    http://www.python-forum.de/topic-10600.html (de)

    :copyleft: 2007 by Jens Diemer
    :license: GNU GPL
"""

import os, sys

# insert django to the sys.path (optional):
os.chdir("../../pylucid/django/")
sys.path.insert(0, os.getcwd())

from django.core import management
from django.conf import settings

# setup a fake settings module
os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
settings.__file__ = "./django/conf/global_settings.py"

# Use a SQLite memory database for the local test:
settings.DATABASE_ENGINE = "sqlite3"
settings.DATABASE_NAME = ":memory:"

# modify some settings for you tests, if needed:
settings.INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
)

# Create the django database and environment:
print "init django, create tables...",
management.setup_environ(settings)
management.call_command('syncdb', verbosity=0, interactive=False)
print "OK\n"

#______________________________________________________________________________
# Now, you can play. Put your test code here:

from django.contrib.auth.models import User
from django import newforms as forms

UserForm = forms.form_for_model(User)
form = UserForm()
html_code = form.as_p()

print html_code
