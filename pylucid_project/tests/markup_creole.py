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
    http://hg.moinmo.in/moin/1.7/file/tip/MoinMoin/parser/
    http://sheep.art.pl/devel/creole/file/tip
    http://djikiki.googlecode.com/svn/trunk/djikiki/creole/

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

    def test_creole_basic1(self):
        out_string = self._parse("a text line.")
        self.assertEqual(out_string, "<p>a text line.</p>\n\n")

    def test_creole_basic2(self):
        self.assertCreole(r"""
            Force\\linebreak
        """, """
            <p>Force<br />
            linebreak</p>
        """)

    def test_creole_basic3(self):
        self.assertCreole(r"""
            Basics: **bold** or //italic//
            or **//both//** or //**both**//
        """, """
            <p>Basics: <b>bold</b> or <i>italic</i><br />
            or <b><i>both</i></b> or <i><b>both</b></i></p>
        """)

    def test_creole_basic4(self):
        self.assertCreole(r"""
            Here is [[a internal]] link.
            This is [[http://domain.tld|external links]].
            A [[internal links|different]] link name.
        """, """
            <p>Here is <a href="a internal">a internal</a> link.<br />
            This is <a href="http://domain.tld">external links</a>.<br />
            A <a href="internal links">different</a> link name.</p>
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
            {{{
            //This// does **not** get [[formatted]]
            }}}
        """, """
            <pre>
            //This// does **not** get [[formatted]]
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
        """, """
            <p>111<br />
            222</p>

            <pre>
            333
            </pre>
            <p>444</p>
        """)

    def test_bold_italics(self):
        self.assertCreole(r"""
            **//bold italics//**
            //**bold italics**//
            //This is **also** good.//
        """, """
            <p><b><i>bold italics</i></b><br />
            <i><b>bold italics</b></i><br />
            <i>This is <b>also</b> good.</i></p>
        """)

    def test_cross_paragraphs(self):
        self.assertCreole("""
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
        self.assertCreole("""
            = Level 1 (largest) =
            == Level 2 ==
            === Level 3 ===
            ==== Level 4 ====
            ===== Level 5 =====
            ====== Level 6 ======
            === Also level 3
            === Also level 3 =
            === Also level 3 ==
            === **not** //parsed// ===
            No == headline == or?
        """, """
            <h1>Level 1 (largest)</h1>
            <h2>Level 2</h2>
            <h3>Level 3</h3>
            <h4>Level 4</h4>
            <h5>Level 5</h5>
            <h6>Level 6</h6>
            <h3>Also level 3</h3>
            <h3>Also level 3</h3>
            <h3>Also level 3</h3>
            <h3>**not** //parsed//</h3>
            <p>No == headline == or?</p>
        """)

    def test_bullet_list(self):
        self.assertCreole("""
            * Item 1
            ** Item 1.1
            ** Item 1.2
            * Item 2
            ** Item 2.1
            *** Item 3.1
            *** Item 3.2
        """, """
            <ul>
            <li>Item 1
              <ul>
              <li>Item 1.1
              </li>
              <li>Item 1.2
              </li>
              </ul>
            </li>
            <li>Item 2
              <ul>
              <li>Item 2.1
                <ul>
                <li>Item 3.1
                </li>
                <li>Item 3.2
                </li>
                </ul>
              </li>
              </ul>
            </li>
            </ul>
        """)

    def test_number_list(self):
        self.assertCreole("""
            # Item 1
            ## Item 1.1
            # Item 2
        """, """
            <ol>
            <li>Item 1
              <ol>
              <li>Item 1.1
              </li>
              </ol>
            </li>
            <li>Item 2
            </li>
            </ol>
        """)

    def test_horizontal_rule(self):
        self.assertCreole("""
            one
            ----
            two
        """, """
            <p>one</p>
            <hr />
            <p>two</p>
        """)




if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])