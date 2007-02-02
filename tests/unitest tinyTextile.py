#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Unitest für \PyLucid\system\tinyTextile.py


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""


import sys, re, difflib, unittest, traceback



sys.path.insert(0, "../") # PyLucid-Root

from PyLucid.system import tinyTextile


## Ausgabe bei Fehlern
# =1 -> als repr()
# =2 -> roh
#~ VERBOSE = 1
VERBOSE = 2



#_____________________________________________________________________________


class OutBuffer(object):
    """
    Hilfsklasse um Ausgaben erst zwischen zu speichern
    """
    def __init__( self ):
        self.data = []

    def write(self, *txt):
        for i in txt:
            self.data.append(i)

    def get(self):
        return "".join(self.data)


class FakeRender(object):
    def highlight(self, sourcecode_type, code, out):
        out.write(
            "<FakeHighlight '%s'>%s</FakeHighlight>\n" % (sourcecode_type, code)
        )

class FakeRequest(object):
    """
    Zum Test wird ein request-Object mit ein paar Eigenschaften benötigt
    """
    URLs = None
    tools = None
    render = FakeRender()

class FakeResponse(object):
    def write(self, txt):
        print "---[page_msg]--- >>>%s<<<" % txt

    def page_msg(self, *txt):
        self.write("".join([str(i) for i in txt]))



class textileFailure(Exception):
    """
    Eine Spezielle Fehler-Klasse, um textile Fehler besser anzeigen zu lassen
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

            if msg.startswith("u'"):
                msg = msg[2:]

            msg = msg.strip("'")
            try:
                block1, block2 = msg.split("' != '")
            except ValueError:
                msg = self._format_output(msg)
                return (
                    "Fehler in Fehlerausgabe!!! ;)\n"
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

    # Eigene Fehlermeldung
    failureException = textileFailure

    def setUp(self):
        self.fake_requestObj = FakeRequest()
        self.fake_responseObj = FakeResponse()

        self.out = OutBuffer()
        self.textile = tinyTextile.parser(
            self.out, self.fake_requestObj, self.fake_responseObj
        )

    def tearDown(self):
        """Out-Buffer 'resetten'"""
        self.out.data = []

    #_________________________________________________________________________

    def _prepare_text(self, txt):
        """
        Damit Text auch eingerückt auf mehere Zeilen so aussieht, als
        wenn er nicht eingerückt wurde ;)
        """
        # Leerzeilen die durch Einrückung entsteht entfernen
        txt = txt.splitlines()

        if txt[0]!="":
            # Erste Zeile muß leer sein!
            raise "First line not empty!"
        else:
            txt = txt[1:]

        # Tiefe an erster Zeile ermitteln
        count = False
        for count, char in enumerate(txt[0]):
            if char!=" ":
                break

        if count == False:
            raise "second line is empty!"

        # Alle Zeilen zurück einrücken
        txt = [i[count:] for i in txt]

        #~ txt = re.sub("\n {2,}", "\n", txt)
        txt = "\n".join(txt)

        # *ein* \n am Anfang entfernen, wenn vorhanden
        if txt.startswith("\n"): txt = txt[1:]
        # *ein* \n am Ende entfernen, wenn vorhanden
        if txt.endswith("\n"): txt = txt[:-1]
        #~ print repr(txt)
        #~ print "-"*79
        return txt

    #_________________________________________________________________________

    def testSelf(self):
        out1 = self._prepare_text("""
                eine Zeile
                zweite Zeile""")
        self.assertEqual(out1, "eine Zeile\nzweite Zeile")

        out2 = self._prepare_text("""
            eine Zeile
            zweite Zeile
        """)
        self.assertEqual(out2, "eine Zeile\nzweite Zeile")

        out3 = self._prepare_text("""
            eine Zeile

            zweite Zeile
        """)
        self.assertEqual(out3, "eine Zeile\n\nzweite Zeile")

        out4 = self._prepare_text("""
            eine Zeile
                zweite Zeile

        """)
        self.assertEqual(out4, "eine Zeile\n    zweite Zeile\n")

        out5 = self._prepare_text("""
            eine Zeile
                zweite Zeile
            dritte Zeile
        """)
        self.assertEqual(out5, "eine Zeile\n    zweite Zeile\ndritte Zeile")



    def testTextile_text1(self):
        self.textile.parse("test")
        self.assertEqual(self.out.get(), "<p>test</p>\n")

    def testTextile_text2(self):
        test_text = self._prepare_text("""
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
        """)
        self.textile.parse(test_text)
        self.assertEqual(
            self.out.get(),
            self._prepare_text("""
                <p>text block 1<br />
                text block 1 line 2</p>
                <p>text block 2<br />
                text block 2 line 2</p>
                <p>windows 1<br />
                windows 2</p>
                <p>mac 1<br />
                mac 2</p>

            """)
        )

    def testTextile_headline1(self):
        content = self._prepare_text("""
            h1. h-1 headline

            h2. h-2 headline
        """)
        out_test = self._prepare_text("""
            <h1>h-1 headline</h1>
            <h2>h-2 headline</h2>

        """)

        self.textile.parse(content)
        self.assertEqual(self.out.get(), out_test)

    def testTextile_pre(self):
        content = self._prepare_text("""
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
        """)

        out_test = self._prepare_text("""
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

        self.textile.parse(content)
        self.assertEqual(self.out.get(),out_test)

    def testTextile_code1(self):
        content = self._prepare_text("""
            <code=py>
            testcode
            </code>
        """)

        out_test = "<FakeHighlight 'py'>testcode</FakeHighlight>\n"

        self.textile.parse(content)
        self.assertEqual(self.out.get(),out_test)

    def testTextile_code2(self):
        content = self._prepare_text("""
            text above code area
            <code=ext>
            test in code 1
            test in code 2
            </code>
            text line under code area

            some text...
            a inline <code>code area</code> in a text line
            ...some other text
        """)

        out_test = self._prepare_text("""
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

        self.textile.parse(content)
        self.assertEqual(self.out.get(),out_test)

    def testTextile_SourceCode1(self):
        content = self._prepare_text("""
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
        """)

        out_test = self._prepare_text("""
            <FakeHighlight 'python'>class Example():
                def __init__(self, *args, **kwargs):
                    # Text1

                    # Text2
                    a = b + c + 1

                    # text 3
                    # text 4

                    # text 5

                    # text 6</FakeHighlight>
        """)

        self.textile.parse(content)
        self.assertEqual(self.out.get(),out_test)

    def testTextile_escaping(self):
        content = self._prepare_text("""
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

        """)

        out_test = self._prepare_text("""
            <p>text above<br />
            <br />
            &lt;a href="#"&gt;bla&lt;/a&gt;<br />
            &lt;strong&gt;Hier alles Escapen!&lt;/strong&gt;<br />
            <br />
            text line under</p>
            <p>inline &lt;escape&gt; Blabla</p>
            <FakeHighlight \'python\'>print "=="
            print "Huch"
            print "=="</FakeHighlight>
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

        self.textile.parse(content)
        self.assertEqual(self.out.get(),out_test)

    def testTextile_list1(self):
        content = self._prepare_text("""
            text above
            * list1
            ** blub
            * bla
            **** foo
            **** bar

            text line under

        """)

        out_test = self._prepare_text("""
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

        self.textile.parse(content)

        print "DoTo: Listen sind nicht gut eingerückt!"
        out1 = self.out.get()
        out1 = "\n".join([i.strip() for i in out1.splitlines()])

        out2 = "\n".join([i.strip() for i in out_test.splitlines()])

        self.assertEqual(out1,out2)

    def testTextile_list2(self):
        content = self._prepare_text("""
            text above
            # list1
            ## blub
            # bla
            #### foo
            #### bar

            text line under

        """)

        out_test = self._prepare_text("""
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

        self.textile.parse(content)

        print "DoTo: Listen sind nicht gut eingerückt!"
        out1 = self.out.get()
        out1 = "\n".join([i.strip() for i in out1.splitlines()])

        out2 = "\n".join([i.strip() for i in out_test.splitlines()])

        self.assertEqual(out1,out2)




def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(tinyTextileTest))
    return suite



if __name__ == "__main__":
    print
    print ">>> %s - Unitest"
    print "_"*79
    unittest.main()
    sys.exit()



