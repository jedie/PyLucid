# coding: utf-8

"""
    PyLucid lexicon plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    Based on a code snippet from 'sma':
    http://www.python-forum.de/post-145270.html#145270
    
    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

import re

SUB_HTML_RE = re.compile(r"(?u)<(\w+)[^>]*>|(\w+)|</(\w+)>")

class SubHtml(object):
    """
    For replacing words in html code. But only if the word is not in a skip_tag.
    
    >>> class LexiconData(dict):
    ...     def __call__(self, word_lower, word):
    ...         return "*%s*" % word.upper()
    >>> lexicon_data = LexiconData({"foo": None, "bar": None})
    >>> s = SubHtml(lexicon_data, skip_tags=["a"])
    >>> s.process('<html><p><a href="Foo=Bar"><strong>Foo</strong> Bar</a>Foo Bar</p></html>')
    '<html><p><a href="Foo=Bar"><strong>Foo</strong> Bar</a>*FOO* *BAR*</p></html>'
    """
    def __init__(self, lexicon_data, skip_tags=[]):
        # forming a dict from the skip_tags list, for faster lookup
        self.skip_tags = dict([(tag.lower(), None) for tag in skip_tags])
        self.lexicon_data = lexicon_data
        self.in_skip_tag = None

    def sub(self, m):
        if self.in_skip_tag: # We are in a skip_tags
            close_tag = m.group(3)
            if close_tag == self.in_skip_tag: # The last skip_tag was closed
                self.in_skip_tag = None
            return m.group()

        tag = m.group(1) # Open html tag
        if tag:
            if tag.lower() in self.skip_tags:
                self.in_skip_tag = tag
            return m.group()

        word = m.group(2) # A word from the text
        if word:
            word_lower = word.lower()
            if word_lower in self.lexicon_data:
                return self.lexicon_data(word_lower, word)

        return m.group()

    def process(self, html):
        return SUB_HTML_RE.sub(self.sub, html)



if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
    print "DocTest end."
