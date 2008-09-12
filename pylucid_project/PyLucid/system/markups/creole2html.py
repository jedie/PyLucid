# -*- coding: utf-8 -*-

"""
WikiCreole to HTML converter
This program is an example of how the creole.py WikiCreole parser
can be used.

Copyright (c) 2007, Radomir Dopieralski <creole@sheep.art.pl>
:copyleft: 2008 by the PyLucid team, see AUTHORS for more details.

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in
   the documentation and/or other materials provided with the
   distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import re
from creole import Parser

class Rules:
    # For the link targets:
    proto = r'http|https|ftp|nntp|news|mailto|telnet|file|irc'
    extern = r'(?P<extern_addr>(?P<extern_proto>%s):.*)' % proto
    interwiki = r'''
            (?P<inter_wiki> [A-Z][a-zA-Z]+ ) :
            (?P<inter_page> .* )
        '''

class HtmlEmitter:
    """
    Generate HTML output for the document
    tree consisting of DocNodes.
    """

    addr_re = re.compile('|'.join([
            Rules.extern,
            Rules.interwiki,
        ]), re.X | re.U) # for addresses

    def __init__(self, root):
        self.root = root

    def get_text(self, node):
        """Try to emit whatever text is in the node."""

        try:
            return node.children[0].content or ''
        except:
            return node.content or ''

    def html_escape(self, text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def attr_escape(self, text):
        return self.html_escape(text).replace('"', '&quot')

    # *_emit methods for emitting nodes of the document:

    def document_emit(self, node):
        return self.emit_children(node)

    def text_emit(self, node):
        return self.html_escape(node.content)

    def separator_emit(self, node):
        return u'<hr />\n';

    def paragraph_emit(self, node):
        return u'<p>%s</p>\n\n' % self.emit_children(node)

    def bullet_list_emit(self, node):
        return u'<ul>\n%s</ul>\n' % self.emit_children(node)

    def number_list_emit(self, node):
        return u'<ol>\n%s</ol>\n' % self.emit_children(node)

    def list_item_emit(self, node):
        return u'<li>%s</li>\n' % self.emit_children(node)

    def table_emit(self, node):
        return u'<table>\n%s</table>\n' % self.emit_children(node)

    def table_row_emit(self, node):
        return u'<tr>\n%s</tr>\n' % self.emit_children(node)

    def table_cell_emit(self, node):
        return u'\t<td>%s</td>\n' % self.emit_children(node)

    def table_head_emit(self, node):
        return u'\t<th>%s</th>\n' % self.emit_children(node)

    def emphasis_emit(self, node):
        return u'<i>%s</i>' % self.emit_children(node)

    def strong_emit(self, node):
        return u'<b>%s</b>' % self.emit_children(node)

    def header_emit(self, node):
        return u'<h%d>%s</h%d>\n' % (
            node.level, self.html_escape(node.content), node.level)

    def code_emit(self, node):
        return u'<tt>%s</tt>' % self.html_escape(node.content)

    def link_emit(self, node):
        target = node.content
        if node.children:
            inside = self.emit_children(node)
        else:
            inside = self.html_escape(target)
        m = self.addr_re.match(target)
        if m:
            if m.group('extern_addr'):
                return u'<a href="%s">%s</a>' % (
                    self.attr_escape(target), inside)
            elif m.group('inter_wiki'):
                raise NotImplementedError
        return u'<a href="%s">%s</a>' % (
            self.attr_escape(target), inside)

    def image_emit(self, node):
        target = node.content
        text = self.get_text(node)
        m = self.addr_re.match(target)
        if m:
            if m.group('extern_addr'):
                return u'<img src="%s" alt="%s">' % (
                    self.attr_escape(target), self.attr_escape(text))
            elif m.group('inter_wiki'):
                raise NotImplementedError
        return u'<img src="%s" alt="%s">' % (
            self.attr_escape(target), self.attr_escape(text))

    def macro_emit(self, node):
        raise NotImplementedError("Node: %r" % node.content)

    def break_emit(self, node):
        return u"<br />\n"

    def preformatted_emit(self, node):
        return u"<pre>\n%s\n</pre>\n" % self.html_escape(node.content)
    
    #--------------------------------------------------------------------------
    # PyLucid Patch:
    # Pass-through all django template blocktags
    def passthrough_emit(self, node):
        return node.content + "\n"
    #--------------------------------------------------------------------------

    def default_emit(self, node):
        """Fallback function for emitting unknown nodes."""

        raise TypeError

    def emit_children(self, node):
        """Emit all the children of a node."""

        return u''.join([self.emit_node(child) for child in node.children])

    def emit_node(self, node):
        """Emit a single node."""

        emit = getattr(self, '%s_emit' % node.kind, self.default_emit)
        return emit(node)

    def emit(self):
        """Emit the document represented by self.root DOM tree."""

        return self.emit_node(self.root)

if __name__=="__main__":
    """
    http://code.google.com/p/creoleparser/source/browse/trunk/creoleparser/tests.py
    http://hg.moinmo.in/moin/1.7/file/tip/MoinMoin/parser/
    http://sheep.art.pl/devel/creole/file/tip
    http://djikiki.googlecode.com/svn/trunk/djikiki/creole/
    """
    
    txt = """
== Headline

This is **bold**...
Wow...

The current page name: >{{ PAGE.name }}< great?
Some {% lucidTag page_update_list count=10 %} text.

a [[www.google.de|Google]] link
a ((/image.jpg|My Image)) image
a {{/image.jpg|My Image}} image

no image: {{ foo|bar }}!
A picture [[http://google.com | {{ campfire.JPG | campfire.jpg }} ]] as a link.

This should be **not** interpreded, it should //pass-through//:
{% sourcecode py %}
import sys

sys.stdout("Hello World!")
{% endsourcecode %}

{{{
a sourcecode

one line
two lines
}}}
And Text

{% sourcecode py %}
var = "Hello World!"
# Jojojo
#print var
{% endsourcecode %}
"""

    txt = r"""111
222
{{{
333
}}}
444"""

    txt = r"""This should be also interpreded as preformated:

{% sourcecode py %}
import sys

sys.stdout("Hello World!")
{% endsourcecode %}

END"""
    print "-"*80
    document = Parser(txt).parse()
    print "="*80
    def emit(node, ident=0):
        for child in node.children:
            print u"%s%s" % (u" "*ident, child)
            emit(child, ident+4)
    emit(document)
    print "*"*80
    print HtmlEmitter(document).emit()