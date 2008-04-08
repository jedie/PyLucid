#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the tinyTextile markup.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2007-02-02 16:37:31 +0100 (Fr, 02 Feb 2007) $
    $Rev: 824 $
    $Author: JensDiemer $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys, re, difflib, unittest, traceback

import tests
from tests.utils.FakeRequest import get_fake_context

from PyLucid.system.tinyTextile import TinyTextileParser
from PyLucid.system.response import SimpleStringIO

# All tests with sourcecode should run without pygments:
from PyLucid.system import hightlighter
hightlighter.PYGMENTS_AVAILABLE = False


## error output format:
# =1 -> via repr()
# =2 -> raw
#VERBOSE = 1
VERBOSE = 2


#_____________________________________________________________________________



class textileFailure(Exception):
    """
    Special error class: Try to display markup errors in a better way.
    """
    def _format_output(self, txt):
        txt = txt.split("\\n")
        if VERBOSE == 1:
            txt = "".join(['%s\\n\n' % i for i in txt])
        elif VERBOSE == 2:
            txt = "".join(['%s\n' % i for i in txt])
        return txt

    def _diff(self, block1, block2):
        d = difflib.Differ()

        block1 = block1.replace("\\n", "\\n\n").split("\n")
        block2 = block2.replace("\\n", "\\n\n").split("\n")

        diff = d.compare(block1, block2)

        result = ["%2s %s\n" % (line, i) for line, i in enumerate(diff)]
        return "".join(result)

    def __str__(self):
        try:
            msg = self.args[0]

            # strip ' out
            if msg.startswith("u'"):
                msg = msg[2:-1]
            else:
                msg = msg[1:-1]
                
            try:
                block1, block2 = msg.split("' != '")
            except ValueError:
                msg = self._format_output(msg)
                return (
                    "Format error in output\n"
                    "Info:\n%s"
                ) % msg

            #~ block1 = block1.rstrip("\\n")
            #~ block2 = block2.rstrip("\\n")
            diff = self._diff(block1, block2)

            block1 = self._format_output(block1)
            block2 = self._format_output(block2)

            return (
                "\n\n---[Output:]---\n%s\n"
                "---[not equal to:]---\n%s"
                "\n---[diff:]---\n%s"
            ) % (block1, block2, diff)
        except:
            etype, value, tb = sys.exc_info()
            msg = traceback.format_exc(tb)
            return msg


#_____________________________________________________________________________



class tinyTextileTest(unittest.TestCase):

    # Use the own error class from above
    failureException = textileFailure

    def setUp(self):
        self.fake_context = get_fake_context()
        self.out = SimpleStringIO()
        self.textile = TinyTextileParser(self.out, self.fake_context)

    def tearDown(self):
        """ delete the out buffer """
        self.out.data = []

    #_________________________________________________________________________

    def _prepare_text(self, txt):
        """
        prepare the multiline, indentation text.
        """
        txt = txt.splitlines()
        assert txt[0]=="", "First must be empty!"
        txt = txt[1:] # Skip the first line

        # get the indentation level from the first line
        count = False
        for count, char in enumerate(txt[0]):
            if char!=" ":
                break

        assert count != False, "second line is empty!"

        # remove indentation from all lines
        txt = [i[count:] for i in txt]

        #~ txt = re.sub("\n {2,}", "\n", txt)
        txt = "\n".join(txt)

        # strip *one* newline at the begining...
        if txt.startswith("\n"): txt = txt[1:]
        # and strip *one* newline at the end of the text
        if txt.endswith("\n"): txt = txt[:-1]
        #~ print repr(txt)
        #~ print "-"*79
        return txt

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

    def testSelf(self):
        out1 = self._prepare_text("""
                one line
                line two""")
        self.assertEqual(out1, "one line\nline two")

        out2 = self._prepare_text("""
            one line
            line two
        """)
        self.assertEqual(out2, "one line\nline two")

        out3 = self._prepare_text("""
            one line

            line two
        """)
        self.assertEqual(out3, "one line\n\nline two")

        out4 = self._prepare_text("""
            one line
                line two

        """)
        self.assertEqual(out4, "one line\n    line two\n")

        out5 = self._prepare_text("""
            one line
                line two
            dritte Zeile
        """)
        self.assertEqual(out5, "one line\n    line two\ndritte Zeile")

    #_________________________________________________________________________

    def testTextile_text1(self):
        out_string = self._parse("text")
        self.assertEqual(out_string, "<p>text</p>\n")

    def testTextile_text2(self):
        self.assertTinyTextile("""
            one line
        """, """
            <p>one line</p>\n
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
            </pre>
            <p>text line under pre area</p>
            <p>some text...<br />
            a inline <pre>pre area</pre> in a text line<br />
            ...some other text</p>

        """)

#    def testTextile_code1(self):
#        self.assertTinyTextile("""
#            <code=py>
#            testcode
#            </code>
#        """)
#
#        out_test = self._prepare_text("""
#            <fieldset class="pygments_code"><legend class="pygments_code">py</legend>
#            <pre><code>testcode</code></pre>
#            </fieldset>
#        """)
#
#        self.textile.parse(content)
#        self.assertEqual(self.out.getvalue(),out_test)

    def testTextile_code2(self):
        self.assertTinyTextile("""
            text above code area
            <code=ext>
            test in code 1
            test in code 2
            </code>
            text line under code area

            some text...
            a inline <code>code area</code> in a text line
            ...some other text
        """, """
            <p>text above code area<br />
            <code=ext><br />
            test in code 1<br />
            test in code 2<br />
            </code></p>
            <p>text line under code area</p>
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

                    # text 5

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

                    # text 5

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




if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])