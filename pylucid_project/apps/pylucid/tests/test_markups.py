#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    TODO:
        * Test other markups than only creole ;)
    
    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os


if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


from pylucid_project.apps.pylucid.markup import MARKUP_CREOLE
from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageContent


class MarkupTestCase(basetest.BaseUnittest, basetest.MarkupTestHelper):
    def _pre_setup(self, *args, **kwargs):
        super(MarkupTestCase, self)._pre_setup(*args, **kwargs)

        self.page_content = PageContent.objects.all()[0]
        self.url = self.page_content.get_absolute_url()

    def _compare_content(self, markup_content, html):
        self.page_content.content = markup_content
        self.page_content.save()

        response = self.client.get(self.url)
        self.assertResponse(response,
            must_contain=(html,),
            must_not_contain=("Traceback",)
        )


class CreoleMarkupTest(MarkupTestCase):
    def _pre_setup(self, *args, **kwargs):
        super(CreoleMarkupTest, self)._pre_setup(*args, **kwargs)
        self.page_content.markup = MARKUP_CREOLE
        self.page_content.save()

    def test_base(self):
        self._compare_content(
            markup_content=self._prepare_text("""
                //Hello **World**!//
                creole is cool!
            """),
            html=self._prepare_text("""
                <p><i>Hello <strong>World</strong>!</i><br />
                creole is cool!</p>
            """),
        )

    def test_singleline_pre(self):
        self._compare_content(
            markup_content="one {{{ **two** }}} **tree**!",
            html="<p>one <pre> **two** </pre> <strong>tree</strong>!</p>",
        )

    def test_multiline_pre(self):
        self._compare_content(
            markup_content=self._prepare_text("""
                start paragraph
                {{{
                one
                two
                }}}
                the end...
            """),
            html=self._prepare_text("""
                <p>start paragraph</p>
                <pre>
                one
                two
                </pre>
                <p>the end...</p>
            """),
        )


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
#    management.call_command('test', "pylucid.tests.test_i18n.TestI18n.test_page_without_lang", verbosity=2)
    management.call_command('test', __file__,
        verbosity=2,
        failfast=True
    )
