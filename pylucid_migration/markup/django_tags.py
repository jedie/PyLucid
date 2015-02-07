# coding: utf-8


"""
    django tag assembler
    ~~~~~~~~~~~~~~~~~~~~

    -cut out django template tags from text.
    -reassembly cut out parts into text.

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import re
from django.utils.safestring import mark_safe, mark_for_escaping

RE_CREOLE_IMAGE=r'(?P<creole_image> {{ .+?(.jpg|.jpeg|.gif|.png).*? }} )'
RE_CREOLE_PRE_INLINE=r'(?P<creole_pre_inline> {{{ (\n|.)*? }}} )'
RE_BLOCK=r'''
    (?P<block>
        \{% \s* (?P<pass_block_start>.+?) .*? %\}
        (\n|.)*?
        \{% \s* end(?P=pass_block_start) \s* %\}
    )
'''
RE_TAG=r'(?P<tag>\{% [^\{\}]*? %\})'
RE_VAR=r'(?P<variable>\{\{ [^\{\}]*? \}\})'


# FIXME: How can we better match on creole image, without a list of known image extensions?
CUT_OUT_RE = re.compile("|".join([
    RE_CREOLE_IMAGE,
    RE_CREOLE_PRE_INLINE,
    RE_BLOCK,
    RE_TAG,
    RE_VAR,
]), re.VERBOSE | re.UNICODE | re.MULTILINE | re.IGNORECASE)

BLOCK_RE=re.compile(r'''
    \{% \s* (?P<pass_block_start>.+?) (?P<args>.*?) %\}
    (?P<content>(\n|.)*?)
    \{% \s* end(?P=pass_block_start) \s* %\}
''', re.VERBOSE | re.UNICODE | re.MULTILINE | re.IGNORECASE)

# Ignore this re groups:
LEAVE_KEYS = ("creole_image", "creole_pre_inline")

# Cut out this re groups:
CUT_OUT_KEYS = ("block", "tag", "variable")

ALL_KEYS = LEAVE_KEYS + CUT_OUT_KEYS

ESCAPE = ("Tag", "TagTag") # For mask existing placeholder
PLACEHOLDER_CUT_OUT = u"DjangoTag%iAssembly"


class PartBase(object):
    def __unicode__(self):
        return u"<Part %s: %r>" % (self.kind, self.content)
    def __str__(self):
        return self.__unicode__()
    def __repr__(self):
        return self.__unicode__()


class PartText(PartBase):
    kind="text"
    def __init__(self, content):
        self.content = mark_safe(content)


class PartTag(PartBase):
    kind="tag"
    def __init__(self, content):
        self.content = mark_for_escaping(content)


class PartBlockTag(PartBase):
    kind="blocktag"
    def __init__(self, tag, args, content):
        self.tag=tag
        self.args=args
        self.content = mark_for_escaping(content)
    def __unicode__(self):
        return u"<Part %s %r %r: %r>" % (self.kind, self.tag, self.args, self.content)


class DjangoTagAssembler(object):

    def __init__(self):
        self.cut_data = []

    def cut_out(self, text, escape):
        def cut(match):
            groups = match.groupdict()

            for key in ALL_KEYS:
                if groups[key] != None:
                    data = groups[key]
                    if key in LEAVE_KEYS:
                        # Don't replace this re match
                        return data
                    data = data.replace(ESCAPE[1], ESCAPE[0])
                    cut_out_pos = len(self.cut_data)
                    self.cut_data.append(data)
                    return PLACEHOLDER_CUT_OUT % cut_out_pos

        if escape:
            text = text.replace(ESCAPE[0], ESCAPE[1])
        text = CUT_OUT_RE.sub(cut, text)
        return text

    def reassembly(self, text, cut_data):
        for no in range(len(cut_data) - 1, -1, -1):
            data = cut_data[no]
            placeholder = PLACEHOLDER_CUT_OUT % no
            text = text.replace(placeholder, data)
        text = text.replace(ESCAPE[1], ESCAPE[0])
        return text

    def reassembly_splitted(self, text):
        placeholder_dict={}
        for no in range(len(self.cut_data) - 1, -1, -1):
            placeholder_dict[PLACEHOLDER_CUT_OUT % no] = no

        data = re.split(
            r"(%s)" % "|".join(placeholder_dict.keys()),
            text
        )

        splitted = []
        for part in data:
            if part in placeholder_dict:
                no=placeholder_dict[part]
                content=self.cut_data[no]

                match = BLOCK_RE.match(content)
                if match:
                    print(match.groupdict())
                    part = PartBlockTag(
                        tag=match.group("pass_block_start"),
                        args=match.group("args").strip(),
                        content=match.group("content")
                    )
                else:
                    part = PartTag(content=content)
            else:
                if not part:
                    continue
                part = PartText(content=part)

            part.content = part.content.replace(ESCAPE[1], ESCAPE[0])
            splitted.append(part)

        return splitted



if __name__=="__main__":
    from pprint import pprint

#     content="""
# text 1
# {% TagOne %}
# tag one content 1
# tag one content 2
# {% endTagOne %}
# text after block
# here a {{ variable }} and a {% inline tag %} too...
# {% TagOne %}
# tag one B content 1
# tag one B content 2
# {% endTagOne %}
# the end text
# {% lucidTag SiteMap %}
#     """

    content="""
pre text
{% sourcecode ext=".py" %}
print "Python is cool!"
{% endsourcecode %}
post text
here a {{ variable }} and a {% inline tag %} too...
    """

    # content="{% lucidTag SiteMap %}"


    assembler = DjangoTagAssembler()
    text, cut_data = assembler.cut_out(content)
    splitted = assembler.reassembly_splitted(text, cut_data)

    pprint(splitted)

    # print("-"*79)
    # print(repr(blocks))
    # print("-"*79)
    # for block in blocks:
    #     # print(type(block))
    #     print(repr(block))
    #     print("")