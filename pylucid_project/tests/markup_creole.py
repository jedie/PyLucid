#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the creole markup.
    We patches some parts of the creole markup, so it doesn't clash with the
    django template syntax.

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
        self.assertEqual(out_string, "<p>a text line. </p>\n\n")
        
    def test_creole_basic2(self):
        self.assertCreole(r"""
            Force\\linebreak
        """, """
            <p>Force<br />
            linebreak </p>
        """)
        
    def test_creole_basic3(self):
        self.assertCreole(r"""
            Basics: **bold** or //italic//
            or **//both//** or //**both**//
        """, """
            <p>Basics: <b>bold</b> or <i>italic</i> <br />
            or <b><i>both</i></b> or <i><b>both</b></i> </p>
        """)
        
    def test_creole_basic4(self):
        self.assertCreole(r"""
            Here is [[a internal]] link.
            This is [[http://domain.tld|external links]].
            A [[internal links|different]] link name.
        """, """
            <p>Here is <a href="a internal">a internal</a> link. <br />
            This is <a href="http://domain.tld">external links</a>. <br />
            A <a href="internal links">different</a> link name. </p>
        """)
        
    def test_django1(self):
        """
        Test if django template tags are not changed by Creole.
        The Creole image tag use "{{" and "}}", too.
        """
        self.assertCreole(r"""
            The current page name: >{{ PAGE.name }}< great?
            A {% lucidTag page_update_list count=10 %} PyLucid plugin
            
            A [[www.domain.tld|link]].
            a {{/image.jpg|My Image}} image
            
            no image: {{ foo|bar }}!
            picture [[www.domain.tld | {{ foo.JPG | Foo }} ]] as a link
        """, """
            <p>The current page name: &gt;{{ PAGE.name }}&lt; great? <br />
            A {% lucidTag page_update_list count=10 %} PyLucid plugin </p>
            
            <p>A <a href="www.domain.tld">link</a>. <br />
            a <img src="/image.jpg" alt="My Image"> image </p>
            
            <p>no image: {{ foo|bar }}! <br />
            picture <a href="www.domain.tld"><img src="foo.JPG" alt="Foo"></a> as a link </p>
        """)
        
    def test_nowiki1(self):
        """
        Test preformatted text
        """
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
        """
        Test preformatted text
        """
        self.assertCreole(r"""
            111
            222
            
            {{{
            333
            }}}
            
            444
        """, """
            <p>111 <br />
            222 </p>
            
            <pre>
            333
            </pre>
            <p>444 </p>
        """)
    
    def test_preformatted(self):
        """
        Test preformatted text
        """
        self.assertCreole(r"""
            This should be also interpreded as preformated:
            
            {% sourcecode py %}
            import sys
            
            sys.stdout("Hello World!")
            {% endsourcecode %}
            
            END
        """, """
            <p>This should be also interpreded as preformated: </p>
            
            {% sourcecode py %}
            import sys
            
            sys.stdout("Hello World!")
            {% endsourcecode %}
            
            <p>END </p>
        """)



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])