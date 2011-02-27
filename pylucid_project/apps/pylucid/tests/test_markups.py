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


class PageContentCreoleMarkupTest(MarkupTestCase):
    def _pre_setup(self, *args, **kwargs):
        super(PageContentCreoleMarkupTest, self)._pre_setup(*args, **kwargs)
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

    def test_image_link_without_title(self):
        self._compare_content(
            markup_content="foo {{/path/to/image.jpg}} bar",
            html='<p>foo <img src="/path/to/image.jpg" alt="/path/to/image.jpg" /> bar</p>',
        )
        
    def test_image_link_with_title(self):
        self._compare_content(
            markup_content="1 {{/path/to/image.jpg|image title}} one",
            html='<p>1 <img src="/path/to/image.jpg" alt="image title" /> one</p>'
        )
        
    def test_image_upcase_extension(self):
        self._compare_content(
            markup_content=self._prepare_text("""
                1 {{/path/to/image.PNG}} one
                2 {{IMAGE.GIF|test}} two
            """),
            html=self._prepare_text("""
                <p>1 <img src="/path/to/image.PNG" alt="/path/to/image.PNG" /> one<br />
                2 <img src="IMAGE.GIF" alt="test" /> two</p>                
            """)
        )
        
    def test_singleline_pre(self):
        self._compare_content(
            markup_content="one {{{ **two** }}} **tree**!",
            html="<p>one <tt> **two** </tt> <strong>tree</strong>!</p>",
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
