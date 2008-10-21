# -*- coding: utf-8 -*-
"""
    PyLucid unittest addons
    ~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""
import sys, unittest, difflib, traceback

## error output format:
# =1 -> via repr()
# =2 -> raw
#VERBOSE = 1
VERBOSE = 2


class MarkupDiffFailure(Exception):
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
            raw_msg = self.args[0]
            
            """
            Get the right split_string is not easy. There are three kinds:
            "foo" != "bar"
            'foo' != "bar"
            "foo" != 'bar'
            'foo' != 'bar'
            With and without a 'u' ;)
            """
            msg = raw_msg.lstrip("u")
            
            first_quote = msg[0]
            second_quote  = msg[-1]
            
            msg = msg.strip("'\"")
            
            split_string = "%s != %s" % (first_quote, second_quote)

            if split_string not in msg:
                # Second part is unicode?
                split_string = "%s != u%s" % (first_quote, second_quote)
                
            if split_string not in msg:
                msg = (
                    "Split error output failed!"
                    " - split string >%r< not in message: %r"
                ) % (split_string, raw_msg)
                raise AssertionError(msg)
               
            try:
                block1, block2 = msg.split(split_string)
            except ValueError, err:
                msg = self._format_output(msg)
                return (
                    "Can't split error output: %r\n"
                    "Info:\n%s"
                ) % (err, msg)

            #~ block1 = block1.rstrip("\\n")
            #~ block2 = block2.rstrip("\\n")
            diff = self._diff(block1, block2)

            block1 = self._format_output(block1)
            block2 = self._format_output(block2)

            return (
                "%r\n\n---[Output:]---\n%s\n"
                "---[not equal to:]---\n%s"
                "\n---[diff:]---\n%s"
            ) % (raw_msg, block1, block2, diff)
        except:
            etype, value, tb = sys.exc_info()
            msg = traceback.format_exc(tb)
            return msg


class MarkupTest(unittest.TestCase):

    # Use the own error class from above
    failureException = MarkupDiffFailure
    
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
    
    def testSelf(self):
        """
        Test for self._prepare_text()
        """
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