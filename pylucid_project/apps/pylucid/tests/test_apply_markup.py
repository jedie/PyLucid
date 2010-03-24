#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Try to test the ./PyLucid/urls.py re patterns.

    Limits
    ~~~~~~
    Some tests depents on these settings:
        settings.ENABLE_INSTALL_SECTION
        settings.SERVE_STATIC_FILES
    To run all tests, we must switch these variables and reinit django.
    You can run these test script standalone and switch the variable here, see
    settings import down.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2009-05-12 16:47:00 +0200 (Di, 12. Mai 2009) $
    $Rev: 1975 $
    $Author: JensDiemer $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, unittest

if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "pylucid.tests.testutils.test_settings"
    virtualenv_file = "../../../../../../../PyLucid_env/bin/activate_this.py"
    execfile(virtualenv_file, dict(__file__=virtualenv_file))

from django.conf import settings



class FakePageMsg(object):
    def __call__(self, *txt):
        print txt

class TestApplyMarkup(unittest.TestCase):
    """
    reverse test
    ~~~~~~~~~~~~
    Test the url re patterns via django.core.urlresolvers.reverse
    """
    def test_html(self):
        from pylucid_project.apps.pylucid.markup.converter import apply_markup
        from pylucid_project.apps.pylucid.models import PageContent
        content = apply_markup(raw_content="<h1>Hello World</h1>", markup_no=PageContent.MARKUP_HTML,
            page_msg=FakePageMsg(), escape_django_tags=False
        )
        self.failUnlessEqual(content, "<h1>Hello World</h1>")

    def test_html(self):
        from pylucid_project.apps.pylucid.markup.converter import apply_markup
        from pylucid_project.apps.pylucid.models import PageContent
        raw_content = (
            "test\n"
            "<<code=.html>>\n"
            "<h1>Hello World</h1>"
            "{% lucidTag foo %}\n"
            "<</code>>"
        )
        content = apply_markup(raw_content, markup_no=PageContent.MARKUP_CREOLE,
            page_msg=FakePageMsg(), escape_django_tags=False
        )
        self.failUnlessEqual(content, "<h1>Hello World</h1>")


if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', "pylucid.TestApplyMarkup")
