# coding: utf-8

"""
    PyLucid lexicon plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    Related threads in german python forum:
        http://www.python-forum.de/topic-19964.html
        http://www.python-forum.de/topic-22102.html    
   
    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import os
import re
import HTMLParser
from xml.sax.saxutils import quoteattr


if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"
    virtualenv_file = "../../../../../bin/activate_this.py"
    execfile(virtualenv_file, dict(__file__=virtualenv_file))



class NoneHTMLParser(object, HTMLParser.HTMLParser):
    """
    Parse the html code with HTMLParser and rebuilt it in self.html
    FIXME: Changes from original html to regenerated:
        - entityref lile umlaute would be replace with the real character, e.g.: &auml; -> ä
        - spaces can be changed, e.g:
            old: <a  href="foo"  >bar</a>
            new: <a href="foo">bar</a>
            old: <br/>
            new: <br />
        - empty attributes are made xhtml conform, e.g:
            old: <td nowrap>
            new: <td nowarp="nowarp">
        - add quote sign to attributes without quote sign, e.g:
            old: <table border=1>
            new: <table border="1">
        - newlines in tags are removes:
            old: <link\nrel="...
            new: <link rel="...
        - attribute quoting can be changed:
            old: title="foo &quot;bar&quot;"
            new: title='foo "bar"'
    """
    def __init__(self):
        # Note: HTMLPaser is a oldstyle class!
        self.reset() # Initialize and reset this HTMLParser instance.

        self.html = ""

    def _add_attrs(self, attrs):
        if attrs:
            attr_list = []
            for attr, value in attrs:
                if value is None:
                    # convert empty attrs to xhtml conform attributes
                    # e.g.: <td nowrap>  ->>  <td nowarp="nowarp">
                    value = attr
                # FIXME: original quoting can be changed
                # e.g: title="foo &quot;bar&quot;" -> title='foo "bar"'
                value = quoteattr(value)
                attr_list.append('%s=%s' % (attr, value))

            self.html += " " + " ".join(attr_list)

    def handle_startendtag(self, tag, attrs):
#        print "handle start+end tag: %r attrs: %r" % (tag, attrs)
        self.html += "<" + tag
        self._add_attrs(attrs)
        self.html += " />"

    def handle_starttag(self, tag, attrs):
#        print "handle start tag: %r attrs: %r" % (tag, attrs)
        self.html += "<" + tag
        self._add_attrs(attrs)
        self.html += ">"

    def handle_endtag(self, tag):
#        print "handle end tag: %r" % tag
        self.html += "</%s>" % tag

    def handle_charref(self, name):
#        print "handle character reference: %r" % name
        self.html += "&#%s;" % name

    def handle_entityref(self, name):
#        print "handle entity reference: %r" % name
        self.html += "&%s;" % name

    def handle_data(self, data):
#        print "handle data: %r" % data
        self.html += data

    def handle_comment(self, data):
#        print "handle comment: %r" % data
        self.html += "<!--%s-->" % data

    def handle_decl(self, decl):
#        print "handle declaration: %r" % decl
        self.html += "<!%s>" % decl

    def handle_pi(self, data):
        print "handle processing instruction:", data

    def unknown_decl(self, data):
        self.error("unknown declaration: %r" % (data,))



class SubHtml(NoneHTMLParser):
    """
    replace all lexicon words in handle_data()
    """
    def __init__(self, lexicon_data, skip_tags):
        super(SubHtml, self).__init__()

        # forming a dict from the skip_tags list, for faster lookup
        self.skip_tags = dict([(tag.lower(), None) for tag in skip_tags])

        self.lexicon_data = lexicon_data

        self.regex = self._build_regex() # Build the regexp to find all lexicon words

        self.in_skip_tag = None # Storage if we are in a skip_tags

    def _build_regex(self):
        keys = self.lexicon_data.keys()

        # Sort longest to shortest
        keys.sort(cmp=lambda x, y: cmp(len(y), len(x)))

        # match on all existing keys with ignorecase
        regex = re.compile(
            "(?<=[\s\>])(%s)(?=[\s\<\.,:])" % "|".join(keys),
            re.IGNORECASE | re.UNICODE | re.MULTILINE
        )
        return regex

    def handle_starttag(self, tag, attrs):
        super(SubHtml, self).handle_starttag(tag, attrs)
#        print "handle start tag: %r attrs: %r" % (tag, attrs)
        if tag in self.skip_tags:
            self.in_skip_tag = tag

    def handle_endtag(self, tag):
        super(SubHtml, self).handle_endtag(tag)
#        print "handle end tag: %r" % tag
        if tag == self.in_skip_tag:
            self.in_skip_tag = None

    def handle_data(self, data):
#        print "handle data: %r" % data
        if data and data.strip(" \n\t") and self.in_skip_tag is None:
            # data is not empty and we are not in a skip_tag area -> replace lexicon entries
            # call lexicon_data with the match object
            data = " %s " % data # work-a-round: http://www.python-forum.de/viewtopic.php?p=162915#162915 
            data = self.regex.sub(self.lexicon_data, data)
            data = data[1:-1] # work-a-round

        self.html += data



if __name__ == "__main__":
    import urllib2, time
    from pylucid_project.utils.diff import diff_lines

#    import doctest
#    doctest.testmod(verbose=False)
#    print "DocTest end."

    skip_tags = ('a', 'input', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'textarea', 'fieldset')

    class LexiconData(dict):
        def __call__(self, matchobject):
            word = matchobject.group(0)
            print "LexiconData.__call__: %r" % word
            term = self[word.lower()]
            return term + word + term

    lexicon_data = LexiconData({"foo bar": "1", "foo": "2", "bar": "3"})
#    lexicon_data = LexiconData({"match on nothing!": None})

#    url = "http://www.pylucid.org"
#    url = "http://www.google.com"
#    url = "http://www.python.org"
#    url = "http://www.heise.de"
#    url = "http://www.facebook.com"
#
#    print "request %r..." % url,
#    f = urllib2.urlopen(url)
#    html = f.read()
#    f.close()
#    print "OK"

#    html = '<a href="foo" title="here &quot;is a problem&quot; fuck">bar</a>'
    html = '''
<html><p><a href="Foo Bar"><strong>Foo Bar</strong> Bar</a>
one Foo Bar two FOO three BaR four
Here not: Fooo or XbarX
</p></html>
'''

    start_time = time.time()
    s = SubHtml(lexicon_data, skip_tags=["a"])
    s.feed(html)
    s.close()
    print "+++ duration: %.3fsec" % (time.time() - start_time)
    print diff_lines(html, s.html)

#    print "-" * 79
#    print html
#    print "-" * 79
#    print p.html
#    print "-" * 79


