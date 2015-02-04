# coding: utf-8


"""
    django tag assembler
    ~~~~~~~~~~~~~~~~~~~~

    -cut out django template tags from text.
    -reassembly cut out parts into text.

    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import re


# FIXME: How can we better match on creole image, without a list of known image extensions?
CUT_OUT_RE = re.compile(r'''
    (?P<creole_image> {{ .+?(.jpg|.jpeg|.gif|.png).*? }} )
    |
    (?P<creole_pre_inline> {{{ (\n|.)*? }}} )
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
''', re.VERBOSE | re.UNICODE | re.MULTILINE | re.IGNORECASE)

# Ignore this re groups:
LEAVE_KEYS = ("creole_image", "creole_pre_inline")

# Cut out this re groups:
CUT_OUT_KEYS = ("block", "tag", "variable")

ALL_KEYS = LEAVE_KEYS + CUT_OUT_KEYS

ESCAPE = ("Tag", "TagTag") # For mask existing placeholder
PLACEHOLDER_CUT_OUT = u"DjangoTag%iAssembly"


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
                    data = data.replace(ESCAPE[1], ESCAPE[0])
                    cut_out_pos = len(cut_data)
                    cut_data.append(data)
                    return PLACEHOLDER_CUT_OUT % cut_out_pos

        text = text.replace(ESCAPE[0], ESCAPE[1])
        text = CUT_OUT_RE.sub(cut, text)
        return text, cut_data

    def reassembly(self, text, cut_data):
        for no in xrange(len(cut_data) - 1, -1, -1):
            data = cut_data[no]
            placeholder = PLACEHOLDER_CUT_OUT % no
            text = text.replace(placeholder, data)
        text = text.replace(ESCAPE[1], ESCAPE[0])
        return text

