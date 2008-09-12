# -*- coding: iso-8859-1 -*-
"""
    Creole wiki markup parser

    See http://wikicreole.org/ for latest specs.

    Notes:
    * No markup allowed in headings.
      Creole 1.0 does not require us to support this.
    * No markup allowed in table headings.
      Creole 1.0 does not require us to support this.
    * No (non-bracketed) generic url recognition: this is "mission impossible"
      except if you want to risk lots of false positives. Only known protocols
      are recognized.
    * We do not allow ":" before "//" italic markup to avoid urls with
      unrecognized schemes (like wtf://server/path) triggering italic rendering
      for the rest of the paragraph.

    PyLucid Updates by the PyLucid team:
        - Make the image tag match more strict, so it doesn't clash with
            django template tags
        - Add a passthrough for all django template blocktags

    @copyright: 2007 MoinMoin:RadomirDopieralski (creole 0.5 implementation),
                2007 MoinMoin:ThomasWaldmann (updates)
                2008 PyLucid:JensDiemer (PyLucid patches)
    @license: GNU GPL, see COPYING for details.
"""

import re


class Rules:
    """Hold all the rules for generating regular expressions."""

    # For the inline elements:
    proto = r'http|https|ftp|nntp|news|mailto|telnet|file|irc'
    url =  r'''(?P<url>
            (^ | (?<=\s | [.,:;!?()/=]))
            (?P<escaped_url>~)?
            (?P<url_target> (?P<url_proto> %s ):\S+? )
            ($ | (?=\s | [,.:;!?()] (\s | $)))
        )''' % proto
    link = r'''(?P<link>
            \[\[
            (?P<link_target>.+?) \s*
            ([|] \s* (?P<link_text>.+?) \s*)?
            ]]
        )'''

    #--------------------------------------------------------------------------
    # PyLucid patch:
    # The image rule should not match on django template tags! So we make it
    # more restricted.
    # It matches only if...
    # ...image target ends with a picture extention
    # ...separator >|< and the image text exist
    image = r'''(?P<image>
            {{
            (?P<image_target>.+?\.jpg|\.jpeg|\.gif|\.png) \s*
            (\| \s* (?P<image_text>.+?) \s*)?
            }}
        )(?i)'''
    #--------------------------------------------------------------------------

    macro = r'''(?P<macro>
            <<
            (?P<macro_name> \w+)
            (\( (?P<macro_args> .*?) \))? \s*
            ([|] \s* (?P<macro_text> .+?) \s* )?
            >>
        )'''
    code = r'(?P<code> {{{ (?P<code_text>.*?) }}} )'
    emph = r'(?P<emph> (?<!:)// )' # there must be no : in front of the //
                                   # avoids italic rendering in urls with
                                   # unknown protocols
    strong = r'(?P<strong> \*\* )'
    linebreak = r'(?P<linebreak> \\\\ )'
    escape = r'(?P<escape> ~ (?P<escaped_char>\S) )'
    char =  r'(?P<char> . )'

    # For the block elements:
    separator = r'(?P<separator> ^ \s* ---- \s* $ )' # horizontal line
    line = r'(?P<line> ^ \s* $ )' # empty line that separates paragraphs
    head = r'''(?P<head>
            ^
            (?P<head_head>=+) \s*
            (?P<head_text> .*? )
            =* \s*$
        )\n*'''
    text = r'(?P<text> .+ ) (?P<break> (?<!\\)$\n(?!\s*$) )?'
    list = r'''(?P<list>
            ^ [ \t]* ([*][^*\#]|[\#][^\#*]).* $
            ( \n[ \t]* [*\#]+.* $ )*
        )''' # Matches the whole list, separate items are parsed later. The
             # list *must* start with a single bullet.
    item = r'''(?P<item>
            ^ \s*
            (?P<item_head> [\#*]+) \s*
            (?P<item_text> .*?)
            $
        )''' # Matches single list items
    pre = r'''(?P<pre>
            ^{{{ \s* $
            (\n)?
            (?P<pre_text>
                ([\#]!(?P<pre_kind>\w*?)(\s+.*)?$)?
                (.|\n)+?
            )
            (\n)?
            ^}}} \s*$
        )'''
    pre_escape = r' ^(?P<indent>\s*) ~ (?P<rest> \}\}\} \s*) $'

    #--------------------------------------------------------------------------
    # PyLucid patch:
    # Pass-through all django template blocktags
    passthrough = r'''(?P<passthrough>
            ^ \s*{%.*?%}
            (.|\n)+?
            {%.*?%} \s*$
        )'''
    #--------------------------------------------------------------------------

    table = r'''(?P<table>
            ^ \s*
            [|].*? \s*
            [|]? \s*
            $
        )'''

    # For splitting table cells:
    cell = r'''
            \| \s*
            (
                (?P<head> [=][^|]+ ) |
                (?P<cell> (  %s | [^|])+ )
            ) \s*
        ''' % '|'.join([link, macro, image, code])

class Parser:
    """
    Parse the raw text and create a document object
    that can be converted into output using Emitter.
    """
    # For pre escaping, in creole 1.0 done with ~:
    pre_escape_re = re.compile(Rules.pre_escape, re.M | re.X)
    # for link descriptions:
    link_re = re.compile(
        '|'.join([Rules.image, Rules.linebreak, Rules.char]),
        re.X | re.U
    )
    item_re = re.compile(Rules.item, re.X | re.U | re.M) # for list items
    cell_re = re.compile(Rules.cell, re.X | re.U) # for table cells
    # For block elements:
    block_re = re.compile(
        '|'.join([
            #------------------------------------------------------------------
            # PyLucid patch:
            # Pass-through all django template blocktags
            Rules.passthrough,
            #------------------------------------------------------------------
            Rules.line, Rules.head, Rules.separator, Rules.pre, Rules.list,
            Rules.table, Rules.text,
        ]),
        re.X | re.U | re.M
    )
    # For inline elements:
    inline_re = re.compile('|'.join([Rules.link, Rules.url, Rules.macro,
        Rules.code, Rules.image, Rules.strong, Rules.emph, Rules.linebreak,
        Rules.escape, Rules.char]), re.X | re.U)

    def __init__(self, raw):
        self.raw = raw
        self.root = DocNode('document', None)
        self.cur = self.root        # The most recent document node
        self.text = None            # The node to add inline characters to

    def _upto(self, node, kinds):
        """
        Look up the tree to the first occurence
        of one of the listed kinds of nodes or root.
        Start at the node node.
        """
        while node.parent is not None and not node.kind in kinds:
            node = node.parent
        return node

    # The _*_repl methods called for matches in regexps. Sometimes the
    # same method needs several names, because of group names in regexps.

    def _passthrough_repl(self, groups):
        """ Pass-through all django template blocktags """
        self.cur = self._upto(
            self.cur, ('document', 'section', 'blockquote')
        )
        DocNode("passthrough", self.root, groups["passthrough"])
        self.text = None

    def _text_repl(self, groups):
        if self.cur.kind in ('table', 'table_row', 'bullet_list',
            'number_list'):
            self.cur = self._upto(self.cur,
                ('document', 'section', 'blockquote'))
        if self.cur.kind in ('document', 'section', 'blockquote'):
            self.cur = DocNode('paragraph', self.cur)
        self.parse_inline(groups.get('text', ''))
        if groups.get('break') and self.cur.kind in ('paragraph',
            'emphasis', 'strong', 'code'):
            DocNode('break', self.cur, '')
        self.text = None
    _break_repl = _text_repl

    def _url_repl(self, groups):
        """Handle raw urls in text."""
        if not groups.get('escaped_url'):
            # this url is NOT escaped
            target = groups.get('url_target', '')
            node = DocNode('link', self.cur)
            node.content = target
            DocNode('text', node, node.content)
            self.text = None
        else:
            # this url is escaped, we render it as text
            if self.text is None:
                self.text = DocNode('text', self.cur, u'')
            self.text.content += groups.get('url_target')
    _url_target_repl = _url_repl
    _url_proto_repl = _url_repl
    _escaped_url = _url_repl

    def _link_repl(self, groups):
        """Handle all kinds of links."""
        target = groups.get('link_target', '')
        text = (groups.get('link_text', '') or '').strip()
        parent = self.cur
        self.cur = DocNode('link', self.cur)
        self.cur.content = target
        self.text = None
        re.sub(self.link_re, self._replace, text)
        self.cur = parent
        self.text = None
    _link_target_repl = _link_repl
    _link_text_repl = _link_repl

    def _macro_repl(self, groups):
        """Handles macros using the placeholder syntax."""
        name = groups.get('macro_name', '')
        text = (groups.get('macro_text', '') or '').strip()
        node = DocNode('macro', self.cur, name)
        node.args = groups.get('macro_args', '') or ''
        DocNode('text', node, text or name)
        self.text = None
    _macro_name_repl = _macro_repl
    _macro_args_repl = _macro_repl
    _macro_text_repl = _macro_repl

    def _image_repl(self, groups):
        """Handles images and attachemnts included in the page."""
        target = groups.get('image_target', '').strip()
        text = (groups.get('image_text', '') or '').strip()
        node = DocNode("image", self.cur, target)
        DocNode('text', node, text or node.content)
        self.text = None
    _image_target_repl = _image_repl
    _image_text_repl = _image_repl

    def _separator_repl(self, groups):
        self.cur = self._upto(self.cur, ('document', 'section', 'blockquote'))
        DocNode('separator', self.cur)

    def _item_repl(self, groups):
        bullet = groups.get('item_head', u'')
        text = groups.get('item_text', u'')
        if bullet[-1] == '#':
            kind = 'number_list'
        else:
            kind = 'bullet_list'
        level = len(bullet)-1
        lst = self.cur
        # Find a list of the same kind and level up the tree
        while (lst and
                   not (lst.kind in ('number_list', 'bullet_list') and
                        lst.level == level) and
                    not lst.kind in ('document', 'section', 'blockquote')):
            lst = lst.parent
        if lst and lst.kind == kind:
            self.cur = lst
        else:
            # Create a new level of list
            self.cur = self._upto(self.cur,
                ('list_item', 'document', 'section', 'blockquote'))
            self.cur = DocNode(kind, self.cur)
            self.cur.level = level
        self.cur = DocNode('list_item', self.cur)
        self.cur.level = level
        self.parse_inline(text)
        self.text = None
    _item_text_repl = _item_repl
    _item_head_repl = _item_repl

    def _list_repl(self, groups):
        text = groups.get('list', u'')
        self.cur.start_list = True
        self.item_re.sub(self._replace, text)

    def _head_repl(self, groups):
        self.cur = self._upto(self.cur, ('document', 'section', 'blockquote'))
        node = DocNode('header', self.cur, groups['head_text'].strip())
        node.level = len(groups['head_head'])
        self.text = None
    _head_head_repl = _head_repl
    _head_text_repl = _head_repl

    def _table_repl(self, groups):
        row = groups.get('table', '|').strip()
        self.cur = self._upto(self.cur, (
            'table', 'document', 'section', 'blockquote'))
        if self.cur.kind != 'table':
            self.cur = DocNode('table', self.cur)
        tb = self.cur
        tr = DocNode('table_row', tb)

        text = ''
        for m in self.cell_re.finditer(row):
            cell = m.group('cell')
            if cell:
                self.cur = DocNode('table_cell', tr)
                self.text = None
                self.parse_inline(cell)
            else:
                cell = m.group('head')
                self.cur = DocNode('table_head', tr)
                self.text = DocNode('text', self.cur, u'')
                self.text.content = cell.strip('=')
        self.cur = tb
        self.text = None

    def _pre_repl(self, groups):
        self.cur = self._upto(self.cur, ('document', 'section', 'blockquote'))
        kind = groups.get('pre_kind', None)
        text = groups.get('pre_text', u'')
        def remove_tilde(m):
            return m.group('indent') + m.group('rest')
        text = self.pre_escape_re.sub(remove_tilde, text)
        node = DocNode('preformatted', self.cur, text)
        node.sect = kind or ''
        self.text = None
    _pre_text_repl = _pre_repl
    _pre_head_repl = _pre_repl
    _pre_kind_repl = _pre_repl

    def _line_repl(self, groups):
        self.cur = self._upto(self.cur, ('document', 'section', 'blockquote'))

    def _code_repl(self, groups):
        DocNode('code', self.cur, groups.get('code_text', u'').strip())
        self.text = None
    _code_text_repl = _code_repl
    _code_head_repl = _code_repl

    def _emph_repl(self, groups):
        if self.cur.kind != 'emphasis':
            self.cur = DocNode('emphasis', self.cur)
        else:
            self.cur = self._upto(self.cur, ('emphasis', )).parent
        self.text = None

    def _strong_repl(self, groups):
        if self.cur.kind != 'strong':
            self.cur = DocNode('strong', self.cur)
        else:
            self.cur = self._upto(self.cur, ('strong', )).parent
        self.text = None

    def _linebreak_repl(self, groups):
        DocNode('break', self.cur, None)
        self.text = None

    def _escape_repl(self, groups):
        if self.text is None:
            self.text = DocNode('text', self.cur, u'')
        self.text.content += groups.get('escaped_char', u'')

    def _char_repl(self, groups):
        if self.text is None:
            self.text = DocNode('text', self.cur, u'')
        self.text.content += groups.get('char', u'')

    #--------------------------------------------------------------------------

    def _replace(self, match):
        """Invoke appropriate _*_repl method. Called for every matched group."""
        groups = match.groupdict()
        for name, text in groups.iteritems():
            if text is not None:
#                if name != "char": print "%15s: %r" % (name, text)
                replace = getattr(self, '_%s_repl' % name)
                replace(groups)
                return

    def parse_inline(self, raw):
        """Recognize inline elements inside blocks."""
        re.sub(self.inline_re, self._replace, raw)

    def parse_block(self, raw):
        """Recognize block elements."""
        re.sub(self.block_re, self._replace, raw)

    def parse(self):
        """Parse the text given as self.raw and return DOM tree."""
        self.parse_block(self.raw)
        return self.root


    #--------------------------------------------------------------------------
    def debug(self):
        """
        Display the current document tree
        """
        print "_"*80
        print "  document tree:"
        print "="*80
        def emit(node, ident=0):
            for child in node.children:
                print u"%s%s" % (u" "*ident, child)
                emit(child, ident+4)
        emit(self.root)
        print "*"*80
    
    def debug_groups(self, groups):
        print "_"*80
        print "  debug groups:"
        for name, text in groups.iteritems():
            if text is not None:
                print "%15s: %r" % (name, text)
        print "-"*80



#------------------------------------------------------------------------------


class DocNode:
    """
    A node in the document.
    """
    def __init__(self, kind='', parent=None, content=None):
        self.children = []
        self.parent = parent
        self.kind = kind
        self.content = content
        if self.parent is not None:
            self.parent.children.append(self)

    def __str__(self):
#        return "DocNode kind '%s', content: %r" % (self.kind, self.content)
        return "%s: %r" % (self.kind, self.content)


#------------------------------------------------------------------------------


if __name__=="__main__":
    txt = r"""== a headline

Here is [[a internal]] link.
This is [[http://domain.tld|external links]].
A [[internal links|different]] link name.

Basics: **bold** or //italic//
or **//both//** or //**both**//
Force\\linebreak.

The current page name: >{{ PAGE.name }}< great?
A {% lucidTag page_update_list count=10 %} PyLucid plugin

{% sourcecode py %}
import sys

sys.stdout("Hello World!")
{% endsourcecode %}

A [[www.domain.tld|link]].
a {{/image.jpg|My Image}} image

no image: {{ foo|bar }}!
picture [[www.domain.tld | {{ foo.JPG | Foo }} ]] as a link

END"""

    txt = r"""one
----
two"""

    p = Parser(txt)
    document = p.parse()
    p.debug()

    def test_rules(rules, txt):
        def display_match(match):
            groups = match.groupdict()
            for name, text in groups.iteritems():
                if name != "char" and text != None:
                    print "%13s: %r" % (name, text)
        re.sub(rules, display_match, txt)

    print "_"*80
    print "plain block rules match:"
    test_rules(Parser("").block_re, txt)

    print "_"*80
    print "plain inline rules match:"
    test_rules(Parser("").inline_re, txt)

    print "---END---"