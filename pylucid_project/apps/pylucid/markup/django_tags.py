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
    (?P<block>
        {% \s* (?P<pass_block_start>.+?) .*? %}
        (\n|.)*?
        {% \s* end(?P=pass_block_start) \s* %}
    )|(?P<tag>
        {%.*?%}
    )|(?P<variable>
        {{.*?}}
    )
''', re.VERBOSE | re.UNICODE | re.MULTILINE)
CUT_OUT_KEYS = ("block", "tag", "variable")

PLACEHOLDER_CUT_OUT = "DjangoTagAassembly%i"


class DjangoTagAssembler(object):
        
    def cut_out(self, text):
        cut_data = []
        
        def cut(match):
            groups = match.groupdict()
            for key in CUT_OUT_KEYS:
                if groups[key] != None:
                    data = groups[key]
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

<h2>
  <a href="DjangoTagAassembly3">
    DjangoTagAassembly4
  </a>
</h2>
<p>DjangoTagAassembly5</p>""")
        text = self.assembler.reassembly(text2, cut_data)
        self.failUnlessEqual(self.test_text, text)

if __name__ == '__main__':
    unittest.main()
