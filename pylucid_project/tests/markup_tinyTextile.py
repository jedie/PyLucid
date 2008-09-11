#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the tinyTextile markup.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys, re, unittest

import tests
from tests.utils.FakeRequest import get_fake_context
from tests.utils import unittest_addons

from PyLucid.system.markups.tinyTextile import TinyTextileParser
from PyLucid.system.response import SimpleStringIO

# All tests with sourcecode should run without pygments:
from PyLucid.system import hightlighter
hightlighter.PYGMENTS_AVAILABLE = False


## error output format:
# =1 -> via repr()
# =2 -> raw
#VERBOSE = 1
VERBOSE = 2

unittest_addons.VERBOSE = VERBOSE

#_____________________________________________________________________________



class tinyTextileTest(unittest_addons.MarkupTest):

    def setUp(self):
        self.fake_context = get_fake_context()
        self.out = SimpleStringIO()
        self.textile = TinyTextileParser(self.out, self.fake_context)

    def tearDown(self):
        """ delete the out buffer """
        self.out.data = []

    #_________________________________________________________________________

    def _parse(self, txt):
        """
        Apply tinyTextile markup on txt
        """
        self.out._container = [] # delete the out buffer
        self.textile.parse(txt)
        out_string = self.out.getvalue()
        return out_string

    def _processTinyTextile(self, source_string, should_string):
        """
        prepate the given text and apply the markup.
        """
        source = self._prepare_text(source_string)
        should = self._prepare_text(should_string)
        out_string = self._parse(source)
        return out_string, should

    def assertTinyTextile(self, source_string, should_string):
        """
        applies the tinyTextile markup to the given source_string and compairs
        it with the should_string.
        """
        out_string, should = self._processTinyTextile(
            source_string, should_string
        )
        self.assertEqual(out_string, should)

    def assertTinyTextileList(self, source_string, should_string):
        """
        tinyTextile doesn't indented lists well. Here we use a work-a-round.
        """
        out_string, should = self._processTinyTextile(
            source_string, should_string
        )
        def format_output(txt):
            return "\n".join([i.strip() for i in txt.splitlines()])

        out_string = format_output(out_string)
        should = format_output(should)

        self.assertEqual(out_string, should)

    #_________________________________________________________________________

    def testTextile_text1(self):
        out_string = self._parse("text")
        self.assertEqual(out_string, "<p>text</p>\n")

    def testTextile_text2(self):
        self.assertTinyTextile(r"""
            Force\\linebreak
        """, """
            <p>Force<br />linebreak</p>\n
        """)

    def testTextile_text3(self):
        self.assertTinyTextile("""
            text block 1
            text block 1 line 2

            text block 2
            text block 2 line 2
            \r
            windows 1\r
            windows 2\r
            \r
            mac 1\r
            mac 2\r
        """, """
            <p>text block 1<br />
            text block 1 line 2</p>
            <p>text block 2<br />
            text block 2 line 2</p>
            <p>windows 1<br />
            windows 2</p>
            <p>mac 1<br />
            mac 2</p>

        """)

    def testTextile_backslash(self):
        self.assertTinyTextile(r"""
            a windows path:
            C:\windows\foo\bar\
            a linux path:
            /usr/bin/python
            a manuel linebreak\\with two backslashes
        """, r"""
            <p>a windows path:<br />
            C:\windows\foo\bar\<br />
            a linux path:<br />
            /usr/bin/python<br />
            a manuel linebreak<br />with two backslashes</p>

        """)

    def testTextile_headline1(self):
        self.assertTinyTextile("""
            h1. headline A

            Text1

            h2. headline B $%#

            Text2
        """, """
            <h1>headline A</h1>
            <p>Text1</p>
            <h2>headline B $%#</h2>
            <p>Text2</p>

        """)

    def testTextile_pre(self):
        self.assertTinyTextile("""
            text above pre area
            <pre>
            test in pre 1

            test in pre 2

            test in pre 3
            test in pre 4
            no\\line\\break
            </pre>
            text line under pre area

            some text...
            a inline <pre>pre area</pre> in a text line
            ...some other text
        """, """
            <p>text above pre area</p>
            <pre>
            test in pre 1

            test in pre 2

            test in pre 3
            test in pre 4
            no\\line\\break
            </pre>
            <p>text line under pre area</p>
            <p>some text...<br />
            a inline <pre>pre area</pre> in a text line<br />
            ...some other text</p>

        """)

    def testTextile_code1(self):
        self.assertTinyTextile("""
            <code=py>
            testcode
            </code>
        """, """
            <fieldset class="pygments_code">
            <legend class="pygments_code">py</legend>
            <pre><code>testcode</code></pre>
            </fieldset>

        """)

    def testTextile_code2(self):
        self.assertTinyTextile("""
            text above code area 1
            <code=ext>
            test in code 1
            test in code 2
            </code>
            text line under code area 1

            text above code area 2
            <code>
            test in code 1
            test in code 2
            </code>
            text line under code area 2

            some text...
            a inline <code>code area</code> in a text line
            ...some other text
        """, """
            <p>text above code area 1</p>
            <fieldset class="pygments_code">
            <legend class="pygments_code">ext</legend>
            <pre><code>test in code 1
            test in code 2</code></pre>
            </fieldset>
            <p>text line under code area 1</p>
            <p>text above code area 2</p>
            <fieldset class="pygments_code">
            <legend class="pygments_code"></legend>
            <pre><code>test in code 1
            test in code 2</code></pre>
            </fieldset>
            <p>text line under code area 2</p>
            <p>some text...<br />
            a inline <code>code area</code> in a text line<br />
            ...some other text</p>

        """)

    def testTextile_SourceCode1(self):
        """
        A known bug: sourcecode parts doesn't handled well. See doc string in
        tinyTextile.py!
        Here we do a "work-a-round" and delete all linebreaks (\n).
        """

        source_string = """
            <python>
            class Example():
                def __init__(self, *args, **kwargs):
                    # Text1

                    # Text2
                    a = b + c + 1

                    # text 3
                    # text 4

                    # text 5 no\\line\\break

                    # text 6
            </python>
        """
        should_string = """
            <fieldset class="pygments_code">
            <legend class="pygments_code">python</legend>
            <pre><code>class Example():
                def __init__(self, *args, **kwargs):
                    # Text1

                    # Text2
                    a = b + c + 1

                    # text 3
                    # text 4

                    # text 5 no\\line\\break

                    # text 6</code></pre>
            </fieldset>
        """

        out_string, should = self._processTinyTextile(
            source_string, should_string
        )
        def format_output(txt):
            return txt.replace("\n", "")

        out_string = format_output(out_string)
        should = format_output(should)

        self.assertEqual(out_string, should)


    def testTextile_SourceCode2(self):
        """
        A known bug: sourcecode parts doesn't handled well. See doc string in
        tinyTextile.py!
        """
        print (
            "skip testTextile_SourceCode2()"
            " - tinyTextile known sourcecode part bug"
        )
        return

        self.assertTinyTextile("""
            <python>
            class Example():
                def __init__(self, *args, **kwargs):
                    # Text1

                    # Text2
                    a = b + c + 1

                    # text 3
                    # text 4

                    # text 5

                    # text 6
            </python>
        """, """
            <fieldset class="pygments_code">
            <legend class="pygments_code">python</legend>
            <pre><code>class Example():
                def __init__(self, *args, **kwargs):
                    # Text1

                    # Text2
                    a = b + c + 1

                    # text 3
                    # text 4

                    # text 5

                    # text 6</code></pre>
            </fieldset>
        """)

        self.textile.parse(content)
        self.assertEqual(self.out.getvalue(), out_test)

    def testTextile_escaping1(self):
        self.assertTinyTextile("""
            escape ==<ul>== and ==<ol>== with "==" ;)
        """, """
            <p>escape &lt;ul&gt; and &lt;ol&gt; with "==" ;)</p>\n
        """)

    def testTextile_escaping2(self):
        self.assertTinyTextile("""
            text above
            ==
            <a href="#">bla</a>
            <strong>Hier alles Escapen!</strong>
            ==
            text line under

            inline ==<escape>== Blabla

            <python>
            print "=="
            print "Huch"
            print "=="
            </python>
            some text...

            ==
            <code>
            Zeile 1

            Zeile 3

            Zeile 5
            </code>
            ==

        """, """
            <p>text above<br />
            <br />
            &lt;a href="#"&gt;bla&lt;/a&gt;<br />
            &lt;strong&gt;Hier alles Escapen!&lt;/strong&gt;<br />
            <br />
            text line under</p>
            <p>inline &lt;escape&gt; Blabla</p>
            <fieldset class="pygments_code">
            <legend class="pygments_code">python</legend>
            <pre><code>print "=="
            print "Huch"
            print "=="</code></pre>
            </fieldset>
            <p>some text...</p>
            <br />
            &lt;code&gt;<br />
            Zeile 1<br />
            <br />
            Zeile 3<br />
            <br />
            Zeile 5<br />
            &lt;/code&gt;<br />

        """)

    def testTextile_list1(self):
        self.assertTinyTextileList("""
            text above
            * list1
            ** blub
            * bla
            **** foo
            **** bar

            text line under

        """, """
            <p>text above</p>
            <ul>
                <li>list1</li>
                <ul>
                    <li>blub</li>
                </ul>
                <li>bla</li>
                <ul>
                    <ul>
                        <ul>
                            <li>foo</li>
                            <li>bar</li>
                        </ul>
                    </ul>
                </ul>
            </ul>
            <p>text line under</p>

        """)

    def testTextile_list2(self):
        self.assertTinyTextileList("""
            text above
            # list1
            ## blub
            # bla
            #### foo
            #### bar

            text line under

        """, """
            <p>text above</p>
            <ol>
                <li>list1</li>
                <ol>
                    <li>blub</li>
                </ol>
                <li>bla</li>
                <ol>
                    <ol>
                        <ol>
                            <li>foo</li>
                            <li>bar</li>
                        </ol>
                    </ol>
                </ol>
            </ol>
            <p>text line under</p>

        """)

    def testTextile_links_urls(self):
        self.assertTinyTextile("""
            http://domain.dtl
            ftp://domain.dtl
            mailto:name@domain.dtl
        """, """
            <p><a href="http://domain.dtl">http://domain.dtl</a><br />
            <a href="ftp://domain.dtl">ftp://domain.dtl</a><br />
            <a href="mailto:name@domain.dtl">name@domain.dtl</a></p>

        """)

    def testTextile_links_old(self):
        """
        The old tinyTextile link format.
        """
        self.assertTinyTextile("""
            a "link text":http://domain.dtl
            This is a link, too: "Link":#unten
            Shortcut link: [[PageName]] !
        """, """
            <p>a <a href="http://domain.dtl">link text</a><br />
            This is a link, too: <a href="#unten">Link</a><br />
            Shortcut link: <a href="/PageName/">PageName</a> !</p>

        """)

    def testTextile_links_new(self):
        """
        The new tinyTextile link format.
        """
        self.assertTinyTextile("""
            a [http://domain.dtl link text]
            This is a link, too: [#unten Link]
            Shortcut link: [[PageName]] !
        """, """
            <p>a <a href="http://domain.dtl">link text</a><br />
            This is a link, too: <a href="#unten">Link</a><br />
            Shortcut link: <a href="/PageName/">PageName</a> !</p>

        """)

    def testTextile_table1(self):
        self.assertTinyTextile(r"""
            table 1 start
            |=Heading Col 1 |=Heading Col 2         |
            |Cell 1.1       |2 lines\\in Cell 1.2   |
            |Cell 2.1       |Cell 2.2               |
            table 1 end

            |Cell 1.1 |Cell 1.2 |Cell 1.3 |
            |Cell 2.1 |Cell 2.2 |Cell 2.3 |
        """, """
            <p>table 1 start</p>
            <table>
            <tr>
            \t<th>Heading Col 1</th>
            \t<th>Heading Col 2</th>
            </tr>
            <tr>
            \t<td>Cell 1.1</td>
            \t<td>2 lines<br />in Cell 1.2</td>
            </tr>
            <tr>
            \t<td>Cell 2.1</td>
            \t<td>Cell 2.2</td>
            </tr>
            </table>
            <p>table 1 end</p>
            <table>
            <tr>
            \t<td>Cell 1.1</td>
            \t<td>Cell 1.2</td>
            \t<td>Cell 1.3</td>
            </tr>
            <tr>
            \t<td>Cell 2.1</td>
            \t<td>Cell 2.2</td>
            \t<td>Cell 2.3</td>
            </tr>
            </table>
            
        """)


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])