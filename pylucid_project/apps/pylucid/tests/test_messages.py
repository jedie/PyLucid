#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    import pylucid_project
    PYLUCID_BASE_PATH = os.path.abspath(os.path.dirname(pylucid_project.__file__))
    path = os.path.join(PYLUCID_BASE_PATH, "tests", "unittest_plugins")

    os.environ['PYLUCID_ADD_PLUGINS_PATH'] = path
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.http import HttpRequest
from django.contrib.auth.models import Group

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import Language
from pylucid_project.apps.pylucid.models import PageTree


class TestMessages(basetest.BaseUnittest):
    """
    inherited from BaseUnittest:
        - initial data fixtures with default test users
        - self.login()
    """
    def test_anonymous(self):
        self.login("superuser")
        response = self.client.get("/?unittest_plugin=MSG_ERROR")
#        response = self.client.get("/pylucid_admin/plugins/internals/show_internals/")
        self.assertResponse(response,
            must_contain=("<html", "A error messages"),
            must_not_contain=("Traceback",)
        )


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    tests = __file__

    management.call_command('test', tests,
        verbosity=2
    )
