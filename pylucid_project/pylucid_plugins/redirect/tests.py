#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - There exist only "PyLucid CMS" lexicon entry in english and german
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os


if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


from django.conf import settings
from django.core.urlresolvers import reverse

from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageTree


class RedirectPluginTest(basetest.BaseLanguageTestCase):
    def _pre_setup(self, *args, **kwargs):
        """ create some language related attributes """
        super(RedirectPluginTest, self)._pre_setup(*args, **kwargs)

        self.new_plugin_page_url = reverse("PageAdmin-new_plugin_page")
        self.redirectmodel_add_url = reverse("admin:redirect_redirectmodel_add")

        self.login("superuser")

    def test_add_form(self):
        response = self.client.get(self.new_plugin_page_url)
        self.assertResponse(response,
            must_contain=(
                'Create a new plugin page',
                '<option value="pylucid_project.pylucid_plugins.redirect">pylucid_plugins.redirect</option>',
            ),
            must_not_contain=("Traceback",)
        )

    def test_create_plugin_page(self):
        """
        Create a 'redirect' plugin page and check the redirection after this.
        """
        test_slug = "test_redirect"
        destination_url = "http://github.com/jedie/PyLucid"

        response = self.client.post(self.new_plugin_page_url,
            data={'app_label': 'pylucid_project.pylucid_plugins.redirect',
            'design': 1,
            'position': 0,
            'slug': test_slug,
            'urls_filename': 'urls.py'
            }
        )
        url = "http://testserver/en/%s/" % test_slug
        self.assertRedirect(response, url, status_code=302)

        response = self.client.get(url)
        self.assertRedirect(response, "http://testserver" + self.redirectmodel_add_url, status_code=302)

        response = self.client.get(self.redirectmodel_add_url)
        self.assertResponse(response,
            must_contain=(
                "Redirect entry for page: /%s/ doesn&#39;t exist, please create." % test_slug,
                'Add redirect model',
            ),
            must_not_contain=("Traceback",)
        )

        page_tree_id = PageTree.on_site.get(slug=test_slug).id
        response = self.client.post(self.redirectmodel_add_url,
            data={
            "pagetree": page_tree_id,
            "destination_url": destination_url,
            "response_type": 302,
            }
        )
        self.assertRedirect(response,
            "http://testserver" + reverse("admin:redirect_redirectmodel_changelist"),
            status_code=302
        )

        response = self.client.get(url)
        self.assertRedirect(response, destination_url, status_code=302)



if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
#    management.call_command('test', "pylucid_plugins.lexicon.tests.RedirectPluginTest", verbosity=0)
    management.call_command('test', __file__, verbosity=1)
