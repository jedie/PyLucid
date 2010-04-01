#!/usr/bin/env python
# coding: utf-8


import HTMLParser

class HTMLscrapper(HTMLParser.HTMLParser):
    """
    Simple html scrapping.
    
    >>> HTMLscrapper().grab('<link href="foo"></link><a href="bar"></a>', tags=("link","a"), attrs=("href",))
    {'href': ['foo', 'bar']}
    """
    def grab(self, content, tags, attrs):
        self.reset() # Initialize and reset this HTMLParser instance.
        self.tags = tags
        self.attrs = attrs
        self.result = {}

        self.feed(content)
        return self.result

    def handle_starttag(self, tag, attrs):
        if tag not in self.tags:
            return

        attr_dict = dict(attrs)
        for attr, value in attr_dict.iteritems():
            if attr not in self.attrs:
                continue

            if attr not in self.result:
                self.result[attr] = []

            self.result[attr].append(value)




if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
    )
    print "DocTest end."
