#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" blog entry in english and german
    
    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import os
import logging

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.core.urlresolvers import reverse
from django.utils.log import getLogger

from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS
from pylucid_project.tests.test_tools import basetest

#logger = getLogger("pylucid.unittest_plugin")
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())

class TestUnitestPlugin(basetest.BaseUnittest):
    """
    inherited from BaseUnittest:
        - initial data fixtures with default test users
        - self.login()
    """
    def test_if_exist_in_pylucid_plugins_data(self):
        self.failUnless("unittest_plugin" in PYLUCID_PLUGINS)

    def test_if_plugin_exists(self):
        self.login("superuser")
        response = self.client.get("/pylucid_admin/plugins/internals/show_internals/")
        self.assertResponse(response,
            must_contain=(
                "pylucid_project.pylucid_plugins.unittest_plugin", #INSTALLED_APPS
                "/PyLucid_env/src/pylucid/pylucid_project/tests/unittest_plugin", # sys.path 
            ),
            must_not_contain=("Traceback",)
        )

    def test_anonymous(self):
        self.login("superuser")
        response = self.client.get("/?unittest_plugin=MSG_ERROR")
#        response = self.client.get("/pylucid_admin/plugins/internals/show_internals/")
        self.assertResponse(response,
            must_contain=("<html", "A error messages"),
            must_not_contain=("Traceback",)
        )

class TestUnitestPluginPage(basetest.BaseUnittest):

    def _pre_setup(self, *args, **kwargs):
        super(TestUnitestPluginPage, self)._pre_setup(*args, **kwargs)

        self.login("superuser")

        new_plugin_page_url = reverse("PageAdmin-new_plugin_page")
        test_slug = "ut_plugin"
        response = self.client.post(new_plugin_page_url,
            data={'app_label': 'pylucid_project.pylucid_plugins.unittest_plugin',
            'design': 1,
            'position': 0,
            'slug': test_slug,
            'urls_filename': 'urls.py'
            }
        )
        self.url = "http://testserver/en/%s/" % test_slug
        self.assertRedirect(response, self.url, status_code=302)

        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=("New plugin page", "unittest_plugin", "created."),
            must_not_contain=("Traceback",)
        )


    def test_plugin_page(self):
        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=("String response from pylucid_plugins.unittest_plugin.view_root()"),
            must_not_contain=("Traceback",)
        )


if __name__ == "__main__":
    # Run all unittest directly   
    from django.core import management

    tests = "pylucid_project.pylucid_plugins.unittest_plugin.tests"
#    tests = "pylucid_project.pylucid_plugins.unittest_plugin.tests.TestUnitestPlugin.test_if_plugin_exists"
#    tests = "pylucid_project.pylucid_plugins.unittest_plugin.tests.TestUnitestPluginPage"

    management.call_command('test', tests,
        verbosity=2,
#        failfast=True
    )
