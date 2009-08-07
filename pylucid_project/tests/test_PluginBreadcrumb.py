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

from pylucid_project.tests import unittest_plugin
from pylucid_project.tests.test_tools import basetest
from pylucid_project.tests.test_tools.pylucid_test_data import TestLanguages


class PluginBreadcrumbTest(basetest.BaseUnittest):
    def test(self):
        for lang in TestLanguages():
            response = self.client.get(
                "/%s/2-rootpage/2-2-subpage/2-2-1-subpage/" % lang.code,
                HTTP_ACCEPT_LANGUAGE=lang.code
            )
            self.assertResponse(response,
                must_contain=(
                    '<p>You are here:',
                    '<a href="/">Index</a>',
                    '<a href="/%s/2-rootpage/">2-rootpage title' % lang.code,
                    '<a href="/%s/2-rootpage/2-2-subpage/">2-2-subpage title' % lang.code,
                    '<a href="/%s/2-rootpage/2-2-subpage/2-2-1-subpage/">2-2-1-subpage title' % lang.code,
                ),
                must_not_contain=("Traceback", unittest_plugin.views.STRING_RESPONSE,),
            )

    def test_add_link(self):
        """
        A plugin can add a link to the breadcrumb list.
        Use the view pylucid_project.tests.unittest_plugin.views.test_BreadcrumbPlugin()
        """
        for lang in TestLanguages():
            url = "/%s/%s/test_BreadcrumbPlugin/" % (lang.code, unittest_plugin.PLUGIN_PAGE_URL)
            response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang.code)
            added_url = "/%s/%s" % (lang.code, unittest_plugin.views.ADDED_LINK_URL)
            self.assertResponse(response,
                must_contain=(
                    '<a href="%s">%s</a>' % (added_url, unittest_plugin.views.ADDED_LINK_TITLE),
                    unittest_plugin.views.ADDED_LINK_RESPONSE_STRING,
                ),
                must_not_contain=("Traceback",),
            )


if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)
