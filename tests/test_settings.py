# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015-2016 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import tempfile

from pylucid_installer.page_instance_template.example_project.settings import *

TEMP_DIR = tempfile.mkdtemp(prefix="pylucid_unittest_")
DATABASE_NAME=os.path.join(TEMP_DIR, "pylucid_unittest_database.sqlite3")
print("Test database: %r" % DATABASE_NAME)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_NAME,
    }
}