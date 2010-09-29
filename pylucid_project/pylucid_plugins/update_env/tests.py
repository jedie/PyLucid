#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    from django.core import management
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.core.urlresolvers import reverse

from pylucid_project.tests.test_tools import basetest



class UpdateEnvTest(basetest.BaseUnittest):

    def _pre_setup(self, *args, **kwargs):
        """ create some blog articles """
        super(UpdateEnvTest, self)._pre_setup(*args, **kwargs)
        self.status_url = reverse("Update-status")

    def test_anonymous(self):
        response = self.client.get(self.status_url)
        self.assertRedirect(response, url="http://testserver/?auth=login&next_url=" + self.status_url)

    def test_status_page(self):
        self.login("superuser")
        response = self.client.get(self.status_url)
        self.assertResponse(response,
            must_contain=(
                "<title>PyLucid - virtual environment source package status</title>",
                "<pre>commit", "Author:",
                '<a href="/pylucid_admin/plugins/update_env/update/django-tools/">',
                '<a href="/pylucid_admin/plugins/update_env/update/django/">',
                '<a href="/pylucid_admin/plugins/update_env/update/pylucid/">',
            ),
            must_not_contain=("Traceback", "XXX INVALID TEMPLATE STRING")
        )


if __name__ == "__main__":
    # Run all unittest directly
#    management.call_command('test', "pylucid_plugins.design.tests.SwitchDesignTest",
#        verbosity=2,
#        failfast=True
#    )
    management.call_command('test', __file__,
        verbosity=2,
        failfast=True
    )
