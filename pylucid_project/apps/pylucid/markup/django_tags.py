# coding: utf-8

"""
    django tag assembler
    ~~~~~~~~~~~~~~~~~~~~

    -cut out django template tags from text.
    -reassembly cut out parts into text.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re
import unittest


CUT_OUT_RE = re.compile(r'''
    (?P<creole_image>
        \{\{
        .+?(\.jpg|\.jpeg|\.gif|\.png) \s*
        (\| \s* .+? \s*)?
        \}\}
    )
    |
    (?P<creole_pre_inline> {{{ .*? }}} )
    |
    (?P<block>
        \{% \s* (?P<pass_block_start>.+?) .*? %\}
        (\n|.)*?
        \{% \s* end(?P=pass_block_start) \s* %\}
    )
    |
    (?P<tag>
        \{% [^\{\}]*? %\}
    )
    |
    (?P<variable>
        \{\{ [^\{\}]*? \}\}
    )
''', re.VERBOSE | re.UNICODE | re.MULTILINE)

# Ignore this re groups:
LEAVE_KEYS = ("creole_image", "creole_pre_inline")

# Cut out this re groups:
CUT_OUT_KEYS = ("block", "tag", "variable")

ALL_KEYS = LEAVE_KEYS + CUT_OUT_KEYS

PLACEHOLDER_CUT_OUT = u"DjangoTagAassembly%i"


class DjangoTagAssembler(object):

    def cut_out(self, text):
        cut_data = []

        def cut(match):
            groups = match.groupdict()

            for key in ALL_KEYS:
                if groups[key] != None:
                    data = groups[key]
                    if key in LEAVE_KEYS:
                        # Don't replace this re match
                        return data
                    cut_out_pos = len(cut_data)
                    cut_data.append(data)
                    return PLACEHOLDER_CUT_OUT % cut_out_pos

        new_text = CUT_OUT_RE.sub(cut, text)
        return new_text, cut_data

    def reassembly(self, text, cut_data):
        for cut_out_pos, data in enumerate(cut_data):
            placeholder = PLACEHOLDER_CUT_OUT % cut_out_pos
            text = text.replace(placeholder, data)
        return text




class TestDjangoTagAssembler(unittest.TestCase):

    test_text = """{% extends "base_generic.html" %}

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
<p>{{ story.tease|truncatewords:"100" }}</p>"""

    def setUp(self):
        self.assembler = DjangoTagAssembler()

    def test(self):
        text2, cut_data = self.assembler.cut_out(self.test_text)
#        from pprint import pprint
#        pprint(cut_data)
#        print text2
        self.failUnlessEqual(cut_data, ['{% extends "base_generic.html" %}',
             '{% block title %}\nThe page title: {{ section.title }}\n{% endblock %}',
             '{{ section.title }}',
             '{{ story.get_absolute_url }}',
             '{{ story.headline|upper }}',
             '{{ story.tease|truncatewords:"100" }}'
        ])
        self.failUnlessEqual(text2, """DjangoTagAassembly0

DjangoTagAassembly1

<h1>DjangoTagAassembly2</h1>

Don't match {{{ **this** }}} stuff.
Or {{/image.jpg| **that** }} it's from creole markup!

<h2>
  <a href="DjangoTagAassembly3">
    DjangoTagAassembly4
  </a>
</h2>
<p>DjangoTagAassembly5</p>""")
        text = self.assembler.reassembly(text2, cut_data)
        self.failUnlessEqual(self.test_text, text)

    def test_unicode(self):
        input_text = u"äöü {{ test }} äöü"
        text2, cut_data = self.assembler.cut_out(input_text)
        self.failUnlessEqual(cut_data, [u'{{ test }}'])
        self.failUnlessEqual(text2, u"äöü DjangoTagAassembly0 äöü")

        text3 = self.assembler.reassembly(text2, cut_data)
        self.failUnlessEqual(text3, input_text)

if __name__ == '__main__':
    unittest.main()
