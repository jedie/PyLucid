# -*- coding: utf-8 -*-

"""
    html2creole converter
    ~~~~~~~~~~~~~~~~~~~~~
    
    convert html code into creole markup.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
    
from HTMLParser import HTMLParser

BOTH2CREOLE = {
    "p": "\n",
    "br": "\n",
    "i": "//",
    "strong": "**",
    "hr": "----",
    
    "table": "\n",
}
START2CREOLE = {
    "a": "[[",

    "tr": "",
    "td": "|",
    "th": "|",
    
    "h1": "\n= ",
    "h2": "\n== ",
    "h3": "\n=== ",
    "h4": "\n==== ",
    "h5": "\n===== ",
    "h6": "\n====== ",
}
END2CREOLE = {
    "a": "]]",
    
    "tr": "|\n",
    "td": "",
    "th": "",
    
    "h1": "\n",
    "h2": "\n",
    "h3": "\n",
    "h4": "\n",
    "h5": "\n",
    "h6": "\n",
}
ENTITY2HTML = {
    "gt": ">",
    "lt": "<",
}

NO_WIKI_TAGS = ("pre", "tt")

import inspect

class DebugList(list):
    def __init__(self, html2creole):
        self.html2creole = html2creole
        super(DebugList, self).__init__()

    def append(self, item):
#        for stack_frame in inspect.stack(): print stack_frame
            
        line, method = inspect.stack()[1][2:4]
            
        print "%-8s   append: %-35r (%-15s line:%s)" % (
            self.html2creole.getpos(), item,
            method, line
        )
        list.append(self, item)


class Html2Creole(HTMLParser):
    def __init__(self, debug=False):
        HTMLParser.__init__(self)
        
        self.debugging = debug
        if self.debugging:
            print "_"*79
            print "Html2Creole debug is on! print every data append."
            self.result = DebugList(self)
        else:
            self.result = []            
        
        self.__last_tag = None
        self.__inner_block = None
        
        self.__list_level = 0         # list level
        self.__inner_listitem = False # in <li>?
        self.__list_type = ""         # <ul> += "*" or <ol> += "#"
        
        self.__inner_table_cell = False
        
    def _error(self, method, tag):
        print ">>> unknown %s @ %s: %r" % (method, self.getpos(), tag)
    
    def debug(self, method, txt):
        if not self.debugging:
            return
        print "%-8s %8s: %s" % (self.getpos(), method, txt)
        
        
    def _get_markup(self, tag, transdict={}):
        for d in (BOTH2CREOLE, transdict):
            if tag in d:
                return d[tag]

    def handle_starttag(self, tag, attrs):
        self.debug("starttag", "%r atts: %s" % (tag, attrs))
            
        self.__last_tag = tag
        
        if tag in NO_WIKI_TAGS:
            # Staring a pre block
            self.__inner_block = tag
            self.result.append("{{{")
            return
                 
        attr_dict = dict(attrs)
        
        if tag in ("th", "td"):
            self.__inner_table_cell = True
        
        if tag == "a":
            data = "[[%s|" % attr_dict["href"]
        elif tag == "img":
            data = "{{%(src)s|%(alt)s}}" % attr_dict
        elif tag == "ul":
            self.__list_type += "*"
            self.__list_level += 1
            return
        elif tag == "ol":
            self.__list_type += "#"
            self.__list_level += 1
            return
        elif tag == "li":
            self.__inner_listitem = True
            self.result.append(self.__list_type + " ")
            return
        else:
            data = self._get_markup(tag, transdict=START2CREOLE)
        
        if data == None:
            self._error("starttag", tag)
        else:
            self.result.append(data)
        
    def handle_data(self, data):
        self.debug("data", "%r" % data)
        
        def strip_ex_second(data):
            lines = data.split("\n")
            # strip every item, except the first one
            lines = lines[:1] + [line.strip() for line in lines[1:]]
            return "\\\\".join(lines)
               
        if self.__list_level > 0: # we are in <ul> or <ol> list
            if self.__inner_listitem == False: # not in <li>
                data = data.strip()
        
        if self.__inner_listitem or self.__inner_table_cell:
            listitem = strip_ex_second(data)
            self.result.append(listitem)
            return
        
        if self.__inner_block == None:
            data = data.replace("\n", "")
            if data=="":
                return
                   
        self.result.append(data)
    
#    def get_starttag_text(self, *args, **kwargs):
#        print ">>> XXX", args, kwargs
        
    def handle_charref(self, name):
        self.debug("charref", "%r" % name)
        if self.__inner_block != None:
            self.result.append("&#%s;" % name)
        else:
            self._error("charref", name)
        
    def handle_entityref(self, name):
        self.debug("entityref", "%r" % name)
        if name in ENTITY2HTML:
            self.result.append(ENTITY2HTML[name])
        else:
            self._error("entityref", name)
        
    def handle_startendtag(self, tag, attrs):
        self.debug("startendtag", "%r atts: %s" % (tag, attrs))
        attr_dict = dict(attrs)

        if tag == "img":
            data = "{{%(src)s|%(alt)s}}" % attr_dict
        else:
            data = self._get_markup(tag)
                        
        if data == None:
            self._error("startendtag", tag)
        else:
            self.result.append(data)

    def handle_endtag(self, tag):
        self.debug("endtag", "%r" % tag)
        if self.__inner_block != None:
            # We are in a block
            if tag == self.__inner_block:
                # The end of the started end block
                self.__inner_block = None
                if tag in NO_WIKI_TAGS:
                    self.result.append("}}}")
                    return
                else:
                    raise NotImplementedError()
            else:
                # We in a block
                self.result.append(tag)
                return           
        
        if tag in ("ul", "ol"):
            # End of a list
            self.__list_level -= 1
            self.__list_type = self.__list_type[:-1]
            if self.__list_level == 0: # Last close tag
                self.result.append("\n")
            return
        elif tag == "li":
            self.__inner_listitem = False
            self.result.append("\n")
            return
        elif tag in ("th", "td"):
            self.__inner_table_cell = True
        
        data = self._get_markup(tag, transdict=END2CREOLE)
        
        if data == None:
            self._error("endtag", tag)
        else:
            self.result.append(data)
        
    def get(self):
        return "".join(self.result).strip()





#______________________________________________________________________________
import unittest
import sys, difflib, traceback

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



class TestHtml2Creole(MarkupTest):

#    def setUp(self):


    def assertCreole(self, raw_markup, raw_html, debug=False):
        markup = self._prepare_text(raw_markup)
        html = self._prepare_text(raw_html)
        
        h2c = Html2Creole(debug)
        h2c.feed(html)
        out_string = h2c.get()
        
        self.assertEqual(out_string, markup)

    def test_bold_italics(self):
        self.assertCreole(r"""
            **//bold italics//**
            //**bold italics**//
            //This is **also** good.//
        """, """
            <p><strong><i>bold italics</i></strong><br />
            <i><strong>bold italics</strong></i><br />
            <i>This is <strong>also</strong> good.</i></p>
        """,
#            debug=True
        )

    def test_links(self):
        self.assertCreole(r"""
            test link: '[[internal links|link A]]' 1 and
            test link: '[[http://domain.tld|link B]]' 2.
        """, """
            <p>test link: '<a href="internal links">link A</a>' 1 and<br />
            test link: '<a href="http://domain.tld">link B</a>' 2.</p>
        """)

    def test_images(self):
        self.assertCreole(r"""
            a {{/image.jpg|JPG pictures}} and
            a {{/image.jpeg|JPEG pictures}} and
            a {{/image.gif|GIF pictures}} and
            a {{/image.png|PNG pictures}} !
            
            picture [[www.domain.tld|{{foo.JPG|Foo}}]] as a link
        """, """
            <p>a <img src="/image.jpg" alt="JPG pictures"> and<br />
            a <img src="/image.jpeg" alt="JPEG pictures"> and<br />
            a <img src="/image.gif" alt="GIF pictures" /> and<br />
            a <img src="/image.png" alt="PNG pictures" /> !</p>
            
            <p>picture <a href="www.domain.tld"><img src="foo.JPG" alt="Foo"></a> as a link</p>
        """)

    def test_nowiki1(self):
        self.assertCreole(r"""
            this:
            {{{
            //This// does **not** get [[formatted]]
            }}}
            and this: {{{** <i>this</i> ** }}} not, too.
            
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
            <p>and this: <tt>** &lt;i&gt;this&lt;/i&gt; ** </tt> not, too.</p>
            
            <h3>Closing braces in nowiki:</h3>
            <pre>
            if (x != NULL) {
              for (i = 0; i &lt; size; i++) {
                if (x[i] &gt; 0) {
                  x[i]--;
              }}}
            </pre>
        """)
    
    def test_headlines(self):
        self.assertCreole(r"""
            = Level 1 (largest)
            
            == Level 2
            
            === Level 3
            
            ==== Level 4
            
            ===== Level 5
            
            ====== Level 6
            
            === **not** \\ //parsed//
            
            No == headline == or?
        """, r"""
            <h1>Level 1 (largest)</h1>
            <h2>Level 2</h2>
            <h3>Level 3</h3>
            <h4>Level 4</h4>
            <h5>Level 5</h5>
            <h6>Level 6</h6>
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

    def test_list1(self):
        """
        FIXME: Two newlines between a list and the next paragraph :( 
        """
        self.assertCreole(r"""
            ==== List a:
            * a1 item
            ** a1.1 Force\\linebreak
            ** a1.2 item
            *** a1.2.1 item
            *** a1.2.2 item
            * a2 item
            
            
            list 'a' end
            
            ==== List b:
            # b1 item
            ## b1.2 item
            ### b1.2.1 item
            ### b1.2.2 Force\\linebreak1\\linebreak2
            ## b1.3 item
            # b2 item
            
            
            list 'b' end
        """, """
            <h4>List a:</h4>
            <ul>
            <li>a1 item</li>
            <ul>
                <li>a1.1 Force
                linebreak</li>
                <li>a1.2 item</li>
                <ul>
                    <li>a1.2.1 item</li>
                    <li>a1.2.2 item</li>
                </ul>
            </ul>
            <li>a2 item</li>
            </ul>
            <p>list 'a' end</p>
            
            <h4>List b:</h4>
            <ol>
            <li>b1 item</li>
            <ol>
                <li>b1.2 item</li>
                <ol>
                    <li>b1.2.1 item</li>
                    <li>b1.2.2 Force
                    linebreak1
                    linebreak2</li>
                </ol>
                <li>b1.3 item</li>
            </ol>
            <li>b2 item</li>
            </ol>
            <p>list 'b' end</p>
        """,
#            debug=True
        )

    def test_list2(self):
        """ Bold, Italics, Links, Pre in Lists """
        self.assertCreole(r"""
            * **bold** item
            * //italic// item
            
            # item about a [[domain.tld|page link]]
            # {{{//this// is **not** [[processed]]}}}
        """, """
            <ul>
                <li><strong>bold</strong> item</li>
                <li><i>italic</i> item</li>
            </ul>
            <ol>
                <li>item about a <a href="domain.tld">page link</a></li>
                <li><tt>//this// is **not** [[processed]]</tt></li>
            </ol>
        """,
#            debug=True
        )

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
                <th>Headline</th>
                <th>a other<br />
                    headline</th>
                <th>the <strong>big end</strong></th>
            </tr>
            <tr>
                <td>a cell</td>
                <td>a <strong>big</strong> cell</td>
                <td><strong><i>bold italics</i></strong></td>
            </tr>
            <tr>
                <td>next<br />
                    line</td>
                <td>No == headline == or?</td>
                <td></td>
            </tr>
            <tr>
                <td></td>
                <td></td>
                <td>open end</td>
            </tr>
            </table>
            <p>...end</p>
        """,
            debug=True
        )

    #__________________________________________________________________________
    # TODO:

#
#    def test_django(self):
#        self.assertCreole(r"""
#            The current page name: >{{ PAGE.name }}< great?
#            A {% lucidTag page_update_list count=10 %} PyLucid plugin
#            {% block %}
#            FooBar
#            {% endblock %}
#            A [[www.domain.tld|link]].
#            no image: {{ foo|bar }}!
#        """, """
#            <p>The current page name: &gt;{{ PAGE.name }}&lt; great?<br />
#            A {% lucidTag page_update_list count=10 %} PyLucid plugin</p>
#            {% block %}
#            FooBar
#            {% endblock %}
#            <p>A <a href="www.domain.tld">link</a>.<br />
#            no image: {{ foo|bar }}!</p>
#        """)
#
#    def test_escape_char(self):
#        self.assertCreole(r"""
#            ~#1
#            http://domain.tld/~bar/
#            ~http://domain.tld/
#            [[Link]]
#            ~[[Link]]
#        """, """
#            <p>#1<br />
#            <a href="http://domain.tld/~bar/">http://domain.tld/~bar/</a><br />
#            http://domain.tld/<br />
#            <a href="Link">Link</a><br />
#            [[Link]]</p>
#        """)

if __name__ == '__main__':
    unittest.main()

#    h2c = Html2Creole(debug=False)
#    h2c = Html2Creole(debug=True)
#    h2c.feed("""
#<strong>bold 1</strong><i>italic1</i>
#111 <strong>bold 1</strong> 222 <i>italic1</i> 333
#""")
#    print "-"*79
#    print h2c.get()
#    print "-"*79