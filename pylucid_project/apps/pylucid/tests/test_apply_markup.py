#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2009-05-12 16:47:00 +0200 (Di, 12. Mai 2009) $
    $Rev: 1975 $
    $Author: JensDiemer $

    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE.txt for more details.
"""

import os, unittest

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

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

    def test_creole(self):
        from pylucid_project.apps.pylucid.markup.converter import apply_markup
        from pylucid_project.apps.pylucid.models import PageContent
        raw_content = (
            u"test\n"
            "<<code=.html>>\n"
            "<h1>Hello World</h1>"
            "{% lucidTag foo %}\n"
            "<</code>>"
        )
        content = apply_markup(raw_content, markup_no=PageContent.MARKUP_CREOLE,
            page_msg=FakePageMsg(), escape_django_tags=False
        )
        self.failUnlessEqual(content,
            u'<p>test</p>\n<fieldset class="pygments_code">\n'
            '<legend class="pygments_code">HTML</legend>'
            '<table class="pygmentstable"><tr>'
            '<td class="linenos"><div class="linenodiv"><pre>1</pre></div></td>'
            '<td class="code"><div class="pygments">'
            '<pre>'
            '<span class="nt">&lt;h1&gt;</span>Hello World<span class="nt">&lt;/h1&gt;</span>'
            '&#x7B;% lucidTag foo %&#x7D;\n'
            '</pre>'
            '</div>\n</td></tr></table></fieldset>\n\n'

        )


if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=1)
