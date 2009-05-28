# coding: utf-8

"""
    PyLucid breadcrumb plugin unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import test_tools # before django imports!

from django_tools.unittest import unittest_base

from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests import unittest_plugin


class PluginBreadcrumbTest(basetest.BaseUnittest):
    def test(self):
        url = "/2-rootpage/2-2-subpage/2-2-1-subpage/"
        response = self.client.get("/%s%s" % (self.default_lang_code, url))
        self.assertRenderedPage(response, "2-2-1-subpage", url, self.default_lang_code)
        self.assertResponse(response,
            must_contain=(
                '<p>You are here:',
                '<a href="/">Index</a>',                
                '<a href="/de/2-rootpage/">2-rootpage title', 
                '<a href="/de/2-rootpage/2-2-subpage/">2-2-subpage title',
                '<a href="/de/2-rootpage/2-2-subpage/2-2-1-subpage/">2-2-1-subpage title',
            ),
            must_not_contain=("Traceback", unittest_plugin.views.STRING_RESPONSE,),
        )
        
    def test_add_link(self):
        """
        A plugin can add a link to the breadcrumb list.
        Use the view pylucid_project.tests.unittest_plugin.views.test_BreadcrumbPlugin()
        """
        url = "/%s/%s/test_BreadcrumbPlugin/" % (self.default_lang_code, unittest_plugin.PLUGIN_PAGE_URL)
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<a href="%s">%s</a>' % (
                    unittest_plugin.views.ADDED_LINK_URL, unittest_plugin.views.ADDED_LINK_TITLE
                ),
                unittest_plugin.views.ADDED_LINK_RESPONSE_STRING,
            ),
            must_not_contain=("Traceback",),
        )


if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)