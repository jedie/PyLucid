# -*- coding: utf-8 -*-

"""
WikiCreole to HTML converter
This program is an example of how the creole.py WikiCreole parser
can be used.


Copyright (c) 2007, Radomir Dopieralski <creole@sheep.art.pl>

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
        return u"<pre>%s</pre>" % self.html_escape(node.content)

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
    #~ import sys
    #~ document = Parser(unicode(sys.stdin.read(), 'utf-8', 'ignore')).parse()
    #~ sys.stdout.write(HtmlEmitter(document).emit().encode('utf-8', 'ignore'))

    """
    http://code.google.com/p/creoleparser/source/browse/trunk/creoleparser/tests.py
    http://hg.moinmo.in/moin/1.7/file/tip/MoinMoin/parser/
    http://sheep.art.pl/devel/creole/file/tip
    http://djikiki.googlecode.com/svn/trunk/djikiki/creole/
    """

    test1 = u"""
== Textauszeichnung

Das ist **fett** und //kursiv//.
Und noch eine Zeile...

== Links

Ein [[Interner Link ]] und ein normaler Link:
[[http://domain.tld/page/| Link Text]]

----

Bilder mit {{Image.jpg|Ein Bild}} toll.

Eine Liste:
 * eins
 * zwei
 ** drei
 ### Nummer 1
 ### Nummer 2

== Tabelle

  |= Item|= Size|= Price |
  | fish | **big**  |cheap   |
  | crab | small|expesive|

  |= Item|= Size|= Price
  | fish | big  |//cheap//
  | crab | small|**very\\expesive**

== preformatted

{{{
== [[NoWiki]]:
//**don't** format//

Good work!
}}}"""


    test2 = u"""= Top-level heading (1)
== This a test for creole 0.1 (2)
=== This is a Subheading (3)
==== Subsub (4)
===== Subsubsub (5)

The ending equal signs should not be displayed:

= Top-level heading (1) =
== This a test for creole 0.1 (2) ==
=== This is a Subheading (3) ===
==== Subsub (4) ====
===== Subsubsub (5) =====


You can make things **bold** or //italic// or **//both//** or //**both**//.

Character formatting extends across line breaks: **bold,
this is still bold. This line deliberately does not end in star-star.

Not bold. Character formatting does not cross paragraph boundaries.

You can use [[internal links]] or [[http://www.wikicreole.org|external links]],
give the link a [[internal links|different]] name.

Here's another sentence: This wisdom is taken from [[Ward Cunningham's]]
[[http://www.c2.com/doc/wikisym/WikiSym2006.pdf|Presentation at the Wikisym 06]].

Here's a external link without a description: [[http://www.wikicreole.org]]

Be careful that italic links are rendered properly:  //[[http://my.book.example/|My Book Title]]// 

Free links without braces should be rendered as well, like http://www.wikicreole.org/ and http://www.wikicreole.org/users/~example. 

Creole1.0 specifies that http://bar and ftp://bar should not render italic,
something like foo://bar should render as italic.

You can use this to draw a line to separate the page:
----

You can use lists, start it at the first column for now, please...

unnumbered lists are like
* item a
* item b
* **bold item c**

blank space is also permitted before lists like:
  *   item a
 * item b
* item c
 ** item c.a

or you can number them
# [[item 1]]
# item 2
# // italic item 3 //
    ## item 3.1
  ## item 3.2

up to five levels
* 1
** 2
*** 3
**** 4
***** 5

* You can have
multiline list items
* this is a second multiline
list item

You can use nowiki syntax if you would like do stuff like this:

{{{
Guitar Chord C:

||---|---|---|
||-0-|---|---|
||---|---|---|
||---|-0-|---|
||---|---|-0-|
||---|---|---|
}}}

Note: if you look at the source code of the above, you see the escape char (tilde, ~ )
being used to escape the closing triple curly braces. This is to do nowiki nesting in this
wiki which doesn't follow Creole 1.0 yet (closing triple curly braces should be indented
by one space).

You can also use it inline nowiki {{{ in a sentence }}} like this.

!!! Escapes 
Normal Link: http://wikicreole.org/ - now same link, but escaped: ~http://wikicreole.org/ 

Normal asterisks: ~**not bold~**

a tilde alone: ~

a tilde escapes itself: ~~xxx

!! Creole 0.2 

This should be a flower with the ALT text "this is a flower" if your wiki supports ALT text on images:

[{ImagePro src='Red-Flower.jpg' caption='here is a red flower' }]

!! Creole 0.4 

Tables are done like this:

||header col1||header col2
|col1|col2
|you         |can         
|also        |align\\ it. 

You can format an address by simply forcing linebreaks:

My contact dates:\\
Pone: xyz\\
Fax: +45\\
Mobile: abc

!! Creole 0.5 

|| Header title               || Another header title     
| {{{ //not italic text// }}} | {{{ **not bold text** }}} 
| ''italic text''             | __  bold text __          

!! Creole 1.0 

If interwiki links are setup in your wiki, this links to the WikiCreole page about Creole 1.0 test cases: [WikiCreole:Creole1.0TestCases].

"""

    document = Parser(test2).parse()
    print HtmlEmitter(document).emit()


