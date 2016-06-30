# coding: utf-8

"""
    django tag assembler
    ~~~~~~~~~~~~~~~~~~~~

    -cut out django template tags from text.
    -reassembly cut out parts into text.

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import re
import traceback

import pygments
from pygments import lexers

from pylucid_migration.markup.lucidTag import parse_lucidtag

LOG=logging.getLogger(name="PyLucidMigration")

RE_CREOLE_IMAGE = r'(?P<creole_image> {{ .+?(.jpg|.jpeg|.gif|.png).*? }} )'
RE_CREOLE_PRE_INLINE = r'(?P<creole_pre_inline> {{{ (\n|.)*? }}} )'
RE_BLOCK = r'''
    (?P<block>
        \{% \s* (?P<pass_block_start>.+?) .*? %\}
        (\n|.)*?
        \{% \s* end(?P=pass_block_start) \s* %\}
    )
'''
RE_TAG = r'(?P<tag>\{% [^\{\}]*? %\})'
RE_VAR = r'(?P<variable>\{\{ [^\{\}]*? \}\})'
RE_COMMENT = r'(?P<comment>\{\# .*? \#\})'


# FIXME: How can we better match on creole image, without a list of known image extensions?
CUT_OUT_RE = re.compile("|".join([
    RE_CREOLE_IMAGE,
    RE_CREOLE_PRE_INLINE,
    RE_BLOCK,
    RE_TAG,
    RE_VAR,
    RE_COMMENT,
]), re.VERBOSE | re.UNICODE | re.MULTILINE | re.IGNORECASE)

BLOCK_RE = re.compile(r'''
    \{% \s* (?P<pass_block_start>.+?) (?P<args>.*?) %\}
    (?P<content>(\n|.)*?)
    \{% \s* end(?P=pass_block_start) \s* %\}
''', re.VERBOSE | re.UNICODE | re.MULTILINE | re.IGNORECASE)

# Ignore this re groups:
LEAVE_KEYS = ("creole_image", "creole_pre_inline")

# Cut out this re groups:
CUT_OUT_KEYS = ("block", "tag", "variable", "comment")

ALL_KEYS = LEAVE_KEYS + CUT_OUT_KEYS

ESCAPE = ("Tag", "TagTag") # For mask existing placeholder
PLACEHOLDER_CUT_OUT = u"DjangoTag%iAssembly"

PYGMENTS_HTML = """
<fieldset class="pygments_code">
<legend class="pygments_code">%(lexer_name)s</legend>
%(code_html)s
</fieldset>
"""


class PartBase(object):
    content = None
    kind = None

    def __init__(self, content):
        self.content = content

    def __unicode__(self):
        return u"<%s %s: %r>" % (self.__class__.__name__, self.kind, self.content)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()


class PartText(PartBase):
    kind = "text"

class PartDjangoTag(PartBase):
    kind = "django_tag"

class PartDjangoComment(PartBase):
    kind = "django_comment"


class PartBlockTag(PartBase):
    kind = "blocktag"

    def __init__(self, content, tag, args, block_content):
        super(PartBlockTag, self).__init__(content)
        self.tag = tag
        self.args = args
        self.block_content = block_content

    def get_pygments_info(self):
        assert self.tag == "sourcecode"

        source_type = self.args.split('=')[1]
        source_type = source_type.strip(""" '".""")
        # LOG.debug("\n\t\tsource type: %r -> %r", self.args, source_type)

        content = self.block_content.strip()

        try:
            lexer = lexers.get_lexer_by_name(source_type)
        except pygments.util.ClassNotFound:
            try:
                lexer = lexers.guess_lexer(content)
            except pygments.util.ClassNotFound:
                lexer = lexers.get_lexer_by_name("text")

        return content, lexer

    def get_html(self):
        if self.tag == "sourcecode":
            content, lexer = self.get_pygments_info()
            formatter = pygments.formatters.HtmlFormatter(
                linenos=True, style='colorful', cssclass="pygments",
            )
            code = pygments.highlight(content, lexer, formatter)
            code = PYGMENTS_HTML % {"lexer_name": lexer.name, "code_html": code}
            return code
        return "<!-- TODO: %s -->" % self.content

    def __unicode__(self):
        return u"<PartBlockTag tag:%r args:%r content:%r>" % (self.tag, self.args, self.content)


class PartLucidTag(PartBase):
    kind = "lucidtag"

    def __init__(self, content, plugin_name, method_name, method_kwargs):
        super(PartLucidTag, self).__init__(content)
        self.plugin_name = plugin_name
        self.method_name = method_name
        self.method_kwargs = method_kwargs

    def __unicode__(self):
        return u"<PartLucidTag plugin:%r method:%r kwargs:%r>" % (
            self.plugin_name, self.method_name, self.method_kwargs
        )


class DjangoTagAssembler(object):
    def __init__(self):
        self.cut_data = []

    def cut_out(self, text, escape):
        def cut(match):
            groups = match.groupdict()
            # print(groups)

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
        # print(text)
        return text

    def reassembly(self, text, cut_data):
        for no in range(len(cut_data) - 1, -1, -1):
            data = cut_data[no]
            placeholder = PLACEHOLDER_CUT_OUT % no
            text = text.replace(placeholder, data)
        text = text.replace(ESCAPE[1], ESCAPE[0])
        return text

    def reassembly_splitted(self, text):

        if not self.cut_data:
            part = PartText(content=text)
            return [part]

        placeholder_dict = {}
        for no in range(len(self.cut_data) - 1, -1, -1):
            placeholder_dict[PLACEHOLDER_CUT_OUT % no] = no

        data = re.split(
            r"(%s)" % "|".join(placeholder_dict.keys()),
            text
        )

        splitted = []
        for part in data:
            if part in placeholder_dict:
                no = placeholder_dict[part]
                content = self.cut_data[no]

                # print(no, content)
                if content.startswith("{#") and content.endswith("#}"):
                    part = PartDjangoComment(content=content)
                    splitted.append(part)
                    continue

                if content.startswith("{% lucidTag"):
                    try:
                        plugin_name, method_name, method_kwargs = parse_lucidtag(content)
                    except Exception as e:
                        print("ERROR parse lucidTag in line: %r" % content)
                        traceback.print_exc()
                        splitted.append(PartDjangoTag(content=content))
                        continue

                    part = PartLucidTag(
                        content=content,
                        plugin_name=plugin_name,
                        method_name=method_name,
                        method_kwargs=method_kwargs,
                    )
                    splitted.append(part)
                    continue
                else:
                    match = BLOCK_RE.match(content)
                    if match:
                        # print(match.groupdict())
                        part = PartBlockTag(
                            content=content,
                            tag=match.group("pass_block_start"),
                            args=match.group("args").strip(),
                            block_content=match.group("content")
                        )
                    else:
                        part = PartDjangoTag(content=content)
            else:
                if not part:
                    continue
                part = PartText(content=part)

            part.content = part.content.replace(ESCAPE[1], ESCAPE[0])
            splitted.append(part)

        return splitted


if __name__ == "__main__":
    from pprint import pprint

    content = """
text 1
{% TagOne %}
tag one content 1
tag one content 2
{% endTagOne %}
text with {# django comment #} inside!
here a {{ variable }} and a {% inline tag %} too...
this is {# deactivated {{ variable }} and {% inline tag %} too #} isn't it?
{% TagOne %}
tag one B content 1
tag one B content 2
{% endTagOne %}
the end text
{% lucidTag PluginName %}
{% lucidTag PluginName kwarg1="value1" %}
{% lucidTag PluginName.MethodName kwarg1="value1" kwarg2="value2" %}
    """

    # content="""
    # pre text
    # {% sourcecode ext=".py" %}
    # print "Python is cool!"
    # {% endsourcecode %}
    # post text
    # here a {{ variable }} and a {% inline tag %} too...
    # """

    content="{% lucidTag SiteMap %}"
    # content="this is {# deactivated {{ variable }} and {% inline tag %} too #} isn't it?"


    assembler = DjangoTagAssembler()
    text = assembler.cut_out(content, escape=True)
    splitted = assembler.reassembly_splitted(text)

    pprint(splitted)

    # print("-"*79)
    # print(repr(blocks))
    # print("-"*79)
    # for block in blocks:
    #     # print(type(block))
    #     print(repr(block))
    #     print("")