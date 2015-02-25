# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import tempfile

from pylucid_installer.page_instance_template.example_project.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(tempfile.tempdir or ".", 'pylucid_unittest_database'),
    }
}