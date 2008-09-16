#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the creole markup.
    We patches some parts of the creole markup, so it doesn't clash with the
    django template syntax.

    Some Links
    ~~~~~~~~~~
    http://code.google.com/p/creoleparser/source/browse/trunk/creoleparser/tests.py
    http://hg.moinmo.in/moin/1.8/file/tip/MoinMoin/parser/
    http://sheep.art.pl/devel/creole/file/tip
    http://code.google.com/p/djikiki/source/browse/#svn/trunk/djikiki/creole
    http://creoleparser.googlepages.com/cheatsheetplus.html
    http://www.wikicreole.org/creole-sandbox/EditX.jsp?page=Home
    http://www.wikicreole.org/wiki/Sandbox

    Differences to Creole 1.0
    ~~~~~~~~~~~~~~~~~~~~~~~~~
     * italics -> <i> and not <em>

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

#import sys, re, difflib, unittest, traceback

import tests
from tests.utils import unittest_addons

from PyLucid.system.markups.creole import Parser
from PyLucid.system.markups.creole2html import HtmlEmitter


## error output format:
# =1 -> via repr()
# =2 -> raw
#VERBOSE = 1
VERBOSE = 2

unittest_addons.VERBOSE = VERBOSE

#_____________________________________________________________________________

class CreoleTest(unittest_addons.MarkupTest):
    def _parse(self, txt):
        """
        Apply creole markup on txt
        """
        document = Parser(txt).parse()
        out_string = HtmlEmitter(document).emit()
        #print ">>>%r<<<" % out_string
        return out_string

    def _processCreole(self, source_string, should_string):
        """
        prepate the given text and apply the markup.
        """
        source = self._prepare_text(source_string)
        should = self._prepare_text(should_string)
        out_string = self._parse(source)
        return out_string, should

    def assertCreole(self, source_string, should_string):
        """
        applies the tinyTextile markup to the given source_string and compairs
        it with the should_string.
        """
        out_string, should = self._processCreole(
            source_string, should_string
        )
        out_string = out_string.rstrip("\n")
        self.assertEqual(out_string, should)

    #--------------------------------------------------------------------------

    def test_creole_basic(self):
        out_string = self._parse("a text line.")
        self.assertEqual(out_string, "<p>a text line.</p>\n")

    def test_creole_linebreak(self):
        self.assertCreole(r"""
            Force\\linebreak
        """, """
            <p>Force<br />
            linebreak</p>
        """)

    def test_bold_italics(self):
        self.assertCreole(r"""
            **//bold italics//**
            //**bold italics**//
            //This is **also** good.//
        """, """
            <p><strong><i>bold italics</i></strong><br />
            <i><strong>bold italics</strong></i><br />
            <i>This is <strong>also</strong> good.</i></p>
        """)

    def test_internal_links(self):
        self.assertCreole(r"""
            A [[internal]] link...
            ...and [[/a internal]] link.
        """, """
            <p>A <a href="internal">internal</a> link...<br />
            ...and <a href="/a internal">/a internal</a> link.</p>
        """)
        
    def test_external_links(self):
        self.assertCreole(r"""
            With pipe separator:
            1 [[internal links|link A]] test.
            2 [[http://domain.tld|link B]] test.
        """, """
            <p>With pipe separator:<br />
            1 <a href="internal links">link A</a> test.<br />
            2 <a href="http://domain.tld">link B</a> test.</p>
        """)

    def test_bolditalic_links(self):
        self.assertCreole(r"""
            //[[a internal]]//
            **[[Shortcut2|a page2]]**
            //**[[Shortcut3|a page3]]**//
        """, """
            <p><i><a href="a internal">a internal</a></i><br />
            <strong><a href="Shortcut2">a page2</a></strong><br />
            <i><strong><a href="Shortcut3">a page3</a></strong></i></p>
        """)
            


    def test_django1(self):
        """
        Test if django template tags are not changed by Creole.
        The Creole image tag use "{{" and "}}", too.
        We test also the passthrough for all django template blocktags
        """
        self.assertCreole(r"""
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
        """, """
            <p>The current page name: &gt;{{ PAGE.name }}&lt; great?<br />
            A {% lucidTag page_update_list count=10 %} PyLucid plugin</p>
            {% sourcecode py %}
            import sys

            sys.stdout("Hello World!")
            {% endsourcecode %}
            <p>A <a href="www.domain.tld">link</a>.<br />
            a <img src="/image.jpg" alt="My Image"> image</p>
            
            <p>no image: {{ foo|bar }}!<br />
            picture <a href="www.domain.tld"><img src="foo.JPG" alt="Foo"></a> as a link</p>
        """)

    def test_nowiki1(self):
        self.assertCreole(r"""
            this:
            {{{
            //This// does **not** get [[formatted]]
            }}}
            and this: {{{** <i>this</i> ** }}}
            
            === Closing braces in nowiki:
            {{{
            if (x != NULL) {
              for (i = 0; i < size; i++) {
                if (x[i] > 0) {
                  x[i]--;
              }}}
            }}}
        """, """
            <p>this:</p>
            <pre>
            //This// does **not** get [[formatted]]
            </pre>
            <p>and this: <tt>** &lt;i&gt;this&lt;/i&gt; **</tt></p>
            
            <h3>Closing braces in nowiki:</h3>
            <pre>
            if (x != NULL) {
              for (i = 0; i &lt; size; i++) {
                if (x[i] &gt; 0) {
                  x[i]--;
              &#x7D;&#x7D;}
            </pre>
        """)

    def test_nowiki2(self):
        self.assertCreole(r"""
            111
            222
            {{{
            333
            }}}
            444
            
            one
            {{{
            foobar
            }}}
            
            two
        """, """
            <p>111<br />
            222</p>
            <pre>
            333
            </pre>
            <p>444</p>
            
            <p>one</p>
            <pre>
            foobar
            </pre>
            <p>two</p>
        """)

    def test_escape_char(self):
        self.assertCreole(r"""
            ~#1
            http://domain.tld/~bar/
            ~http://domain.tld/
            [[Link]]
            ~[[Link]]
        """, """
            <p>#1<br />
            <a href="http://domain.tld/~bar/">http://domain.tld/~bar/</a><br />
            http://domain.tld/<br />
            <a href="Link">Link</a><br />
            [[Link]]</p>
        """)

    def test_cross_paragraphs(self):
        self.assertCreole(r"""
            Bold and italics should //be
            able// to cross lines.

            But, should //not be...

            ...able// to cross paragraphs.
        """, """
            <p>Bold and italics should <i>be<br />
            able</i> to cross lines.</p>
            
            <p>But, should <i>not be...</i></p>
            
            <p>...able<i> to cross paragraphs.</i></p>
        """)

    def test_headlines(self):
        self.assertCreole(r"""
            = Level 1 (largest) =
            == Level 2 ==
            === Level 3 ===
            ==== Level 4 ====
            ===== Level 5 =====
            ====== Level 6 ======
            === Also level 3
            === Also level 3 =
            === Also level 3 ==
            === **not** \\ //parsed// ===
            No == headline == or?
        """, r"""
            <h1>Level 1 (largest)</h1>
            <h2>Level 2</h2>
            <h3>Level 3</h3>
            <h4>Level 4</h4>
            <h5>Level 5</h5>
            <h6>Level 6</h6>
            <h3>Also level 3</h3>
            <h3>Also level 3</h3>
            <h3>Also level 3</h3>
            <h3>**not** \\ //parsed//</h3>
            <p>No == headline == or?</p>
        """)

    def test_horizontal_rule(self):
        self.assertCreole(r"""
            one
            ----
            two
        """, """
            <p>one</p>
            <hr />
            <p>two</p>
        """)

    def test_bullet_list(self):
        self.assertCreole(r"""
            * Item 1
            ** Item 1.1
            ** a **bold** Item 1.2
            * Item 2
            ** Item 2.1
            *** [[a link Item 3.1]]
            *** Force\\linebreak 3.2
                *** item 3.3
              *** item 3.4
              
            up to five levels
            * 1
            ** 2
            *** 3
            **** 4
            ***** 5
        """, """
            <ul>
            \t<li>Item 1
            \t<ul>
            \t\t<li>Item 1.1</li>
            \t\t<li>a <strong>bold</strong> Item 1.2</li>
            \t</ul></li>
            \t<li>Item 2
            \t<ul>
            \t\t<li>Item 2.1
            \t\t<ul>
            \t\t\t<li><a href="a link Item 3.1">a link Item 3.1</a></li>
            \t\t\t<li>Force<br />
            \t\t\tlinebreak 3.2</li>
            \t\t\t<li>item 3.3</li>
            \t\t\t<li>item 3.4</li>
            \t\t</ul></li>
            \t</ul></li>
            </ul>
            <p>up to five levels</p>
            <ul>
            \t<li>1
            \t<ul>
            \t\t<li>2
            \t\t<ul>
            \t\t\t<li>3
            \t\t\t<ul>
            \t\t\t\t<li>4
            \t\t\t\t<ul>
            \t\t\t\t\t<li>5</li>
            \t\t\t\t</ul></li>
            \t\t\t</ul></li>
            \t\t</ul></li>
            \t</ul></li>
            </ul>
        """)

    def test_number_list(self):
        self.assertCreole(r"""
            # Item 1
            ## Item 1.1
            ## a **bold** Item 1.2
            # Item 2
            ## Item 2.1
            ### [[a link Item 3.1]]
            ### Force\\linebreak 3.2
                ### item 3.3
              ### item 3.4
            
            up to five levels
            # 1
            ## 2
            ### 3
            #### 4
            ##### 5
        """, """
            <ol>
            \t<li>Item 1
            \t<ol>
            \t\t<li>Item 1.1</li>
            \t\t<li>a <strong>bold</strong> Item 1.2</li>
            \t</ol></li>
            \t<li>Item 2
            \t<ol>
            \t\t<li>Item 2.1
            \t\t<ol>
            \t\t\t<li><a href="a link Item 3.1">a link Item 3.1</a></li>
            \t\t\t<li>Force<br />
            \t\t\tlinebreak 3.2</li>
            \t\t\t<li>item 3.3</li>
            \t\t\t<li>item 3.4</li>
            \t\t</ol></li>
            \t</ol></li>
            </ol>
            <p>up to five levels</p>
            <ol>
            \t<li>1
            \t<ol>
            \t\t<li>2
            \t\t<ol>
            \t\t\t<li>3
            \t\t\t<ol>
            \t\t\t\t<li>4
            \t\t\t\t<ol>
            \t\t\t\t\t<li>5</li>
            \t\t\t\t</ol></li>
            \t\t\t</ol></li>
            \t\t</ol></li>
            \t</ol></li>
            </ol>
        """)
        
    def test_list(self):
        """ Bold, Italics, Links, Pre in Lists """
        self.assertCreole(r"""
            * **bold** item
            * //italic// item
            
            # item about a [[certain_page]]
            # {{{ //this// is **not** [[processed]] }}}
        """, """
            <ul>
            \t<li><strong>bold</strong> item</li>
            \t<li><i>italic</i> item</li>
            </ul>
            <ol>
            \t<li>item about a <a href="certain_page">certain_page</a></li>
            \t<li><tt>//this// is **not** [[processed]]</tt></li>
            </ol>
        """)

    def test_table(self):
        self.assertCreole(r"""
            A Table...
            |= Headline  |= a other\\headline    |= the **big end        |
            | a cell     | a **big** cell        |**//bold italics//**   |
            | next\\line | No == headline == or? |                       |
            |            |                       | open end
            ...end
        """, """
            <p>A Table...</p>
            <table>
            <tr>
            \t<th>Headline</th>
            \t<th>a other<br />
            \t\theadline</th>
            \t<th>the <strong>big end</strong></th>
            </tr>
            <tr>
            \t<td>a cell</td>
            \t<td>a <strong>big</strong> cell</td>
            \t<td><strong><i>bold italics</i></strong></td>
            </tr>
            <tr>
            \t<td>next<br />
            \t\tline</td>
            \t<td>No == headline == or?</td>
            \t<td></td>
            </tr>
            <tr>
            \t<td></td>
            \t<td></td>
            \t<td>open end</td>
            </tr>
            </table>
            <p>...end</p>
        """)

    def test_html_lines(self):
        self.assertCreole(r"""
            This is a normal Text block witch would
            escape html chars like < and > ;)
            <p>this <strong class="my">html code</strong> line pass-through</p>
            end
        """, """
            <p>This is a normal Text block witch would<br />
            escape html chars like &lt; and &gt; ;)</p>
            <p>this <strong class="my">html code</strong> line pass-through</p>
            <p>end</p>
        """)




if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])