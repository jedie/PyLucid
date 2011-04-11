#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
        - related test in pylucid_plugins/language/tests.py
    
    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import unittest
from pprint import pprint


if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.markup.django_tags import DjangoTagAssembler


class Test_low_level_DjangoTagAssembler(unittest.TestCase, basetest.MarkupTestHelper):
    def setUp(self):
        self.assembler = DjangoTagAssembler()

    def test1(self):
        test_text = self._prepare_text("""
            {% extends "base_generic.html" %}

            {% block title %}
            The page title: {{ section.title }}
            {% endblock %}
            
            <h1>{{ section.title }}</h1>
            
            Don't match {{{ **this** }}} stuff.
            Or {{/image.jpg| **that** }} it's from creole markup!
            
            <h2>
              <a href="{{ story.get_absolute_url }}">
                {{ story.headline|upper }}
              </a>
            </h2>
            <p>{{ story.tease|truncatewords:"100" }}</p>
        """)

        text2, cut_data = self.assembler.cut_out(test_text)
#        pprint(cut_data)
#        print text2
        self.failUnlessEqual(cut_data, ['{% extends "base_generic.html" %}',
             '{% block title %}\nThe page title: {{ section.title }}\n{% endblock %}',
             '{{ section.title }}',
             '{{ story.get_absolute_url }}',
             '{{ story.headline|upper }}',
             '{{ story.tease|truncatewords:"100" }}'
        ])
        self.failUnlessEqual(text2, self._prepare_text("""
            DjangoTag0Assembly

            DjangoTag1Assembly
            
            <h1>DjangoTag2Assembly</h1>
            
            Don't match {{{ **this** }}} stuff.
            Or {{/image.jpg| **that** }} it's from creole markup!
            
            <h2>
              <a href="DjangoTag3Assembly">
                DjangoTag4Assembly
              </a>
            </h2>
            <p>DjangoTag5Assembly</p>
        """))
        text = self.assembler.reassembly(text2, cut_data)
        self.failUnlessEqual(test_text, text)

    def test_multilinepre(self):
        test_text = u'start paragraph\n{{{\none\ntwo\n}}}\nthe end...'
        text2, cut_data = self.assembler.cut_out(test_text)
#        pprint(cut_data)
#        print text2
        self.failUnlessEqual(cut_data, [])
        self.failUnlessEqual(text2, test_text)

    def test_creole_image(self):
        test_text = u'a {{/image.jpg}} {{image.jpeg|text}}...'
        text2, cut_data = self.assembler.cut_out(test_text)
        self.failUnlessEqual(cut_data, [])
        self.failUnlessEqual(text2, test_text)

    def test_creole_image_upcase(self):
        test_text = u'a {{/IMAGE.PNG}}...'
        text2, cut_data = self.assembler.cut_out(test_text)
#        pprint(cut_data)
#        print text2
        self.failUnlessEqual(cut_data, [])
        self.failUnlessEqual(text2, test_text)

    def test_not_a_creole_image(self):
        test_text = u'a {{ variable|filter:"/" }}...'
        text2, cut_data = self.assembler.cut_out(test_text)
        self.failUnlessEqual(cut_data, [u'{{ variable|filter:"/" }}'])
        self.failUnlessEqual(text2, u"a DjangoTag0Assembly...")

    def test_unicode(self):
        input_text = u"äöü {{ test }} äöü"
        text2, cut_data = self.assembler.cut_out(input_text)
        self.failUnlessEqual(cut_data, [u'{{ test }}'])
        self.failUnlessEqual(text2, u"äöü DjangoTag0Assembly äöü")

        text3 = self.assembler.reassembly(text2, cut_data)
        self.failUnlessEqual(text3, input_text)

    def test_escaping(self):
        test_text = "FooDjangoTag0AssemblyBar {{ Tag }} - {% lucidTag auth %}"

        text2, cut_data = self.assembler.cut_out(test_text)
#        pprint(cut_data)
#        print text2

        self.failUnlessEqual(cut_data, ["{{ Tag }}", "{% lucidTag auth %}"])
        self.failUnlessEqual(text2,
            "FooDjangoTagTag0AssemblyBar DjangoTag0Assembly - DjangoTag1Assembly"
        )

        text = self.assembler.reassembly(text2, cut_data)
        self.failUnlessEqual(test_text, text)


    def test_more_than_ten(self):
        test_text = "\n".join(["{{ %i }}" % no for no in xrange(12)])

        text2, cut_data = self.assembler.cut_out(test_text)
#        pprint(cut_data)
#        print text2

        self.failUnlessEqual(cut_data, ["{{ %i }}" % no for no in xrange(12)])
        self.failUnlessEqual(text2,
            "\n".join(["DjangoTag%iAssembly" % no for no in xrange(12)])
        )

        text = self.assembler.reassembly(text2, cut_data)
        self.failUnlessEqual(test_text, text)




if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
#    management.call_command('test', "pylucid.tests.test_i18n.TestI18n.test_page_without_lang", verbosity=2)
    management.call_command('test', __file__,
        verbosity=2,
        failfast=True
    )
