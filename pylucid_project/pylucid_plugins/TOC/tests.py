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
from django.test import TestCase

from pylucid_project.apps.pylucid.models import PageMeta
from pylucid_project.tests.test_tools import basetest



class TOC_Test(basetest.BaseUnittest):
    def test_toc(self):
        pagemeta = PageMeta.objects.get(name="creole")
        url = pagemeta.get_absolute_url()
        response = self.client.get(url)
        self.assertResponse(response,
            must_contain=(
                '<div class="PyLucidPlugins TOC" id="TOC_lucidTag">',

                '<ol><h3 class="toc_headline">table of contents</h3>',
                '<li><a href="#Top-level-heading-1" title="go down to this section">&darr;&nbsp;Top-level heading (1)</a></li>',

                '<h1 id="Top-level-heading-1" class="headline_anchor">',
                '<a href="#top" title="go top" class="top_link"><span class="uarr">&uarr;&nbsp;</span>Top-level heading (1)</a>',
                '<a title="Permalink to this section" href="/permalink/17/the-buildin-creole-markup#Top-level-heading-1" class="section_anchor">&nbsp;#</a>',
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
