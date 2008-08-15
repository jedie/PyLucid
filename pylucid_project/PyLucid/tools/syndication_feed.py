# -*- coding: utf-8 -*-

"""
    PyLucid feed tools
    ~~~~~~~~~~~~~~~~~~

    Some small tools around syndication feeds.

    Used the django syndication feed framework:
        http://www.djangoproject.com/documentation/syndication_feeds/

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

import os

if __name__ == "__main__":
    # For doctest
    os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"

from django.utils.translation import ugettext as _
from django.utils import feedgenerator

RSS_INFO_LINK = _("http://en.wikipedia.org/wiki/RSS")

FEED_FORMAT_INFO = (
    {
        "ext"      : u"atom",
        "title"    : _("Atom Syndication Format"),
        "generator": feedgenerator.Atom1Feed,
        "info_link": _("http://en.wikipedia.org/wiki/Atom_(standard)")
    },
    {
        "ext"      : u"rss",
        "title"    : _("RSS v2.01rev2 (Really Simple Syndication)"),
        "generator": feedgenerator.Rss201rev2Feed,
        "info_link": RSS_INFO_LINK,
    },
    {
        "ext"      : u"rss091",
        "title"    : _("RSS v0.91 (userland, Rich Site Summary)"),
        "generator": feedgenerator.RssUserland091Feed,
        "info_link": RSS_INFO_LINK,
    },
)
FORMAT_INFO_DICT = dict([(i["ext"], i) for i in FEED_FORMAT_INFO])


class FeedFormat(dict):
    """
    Small helper class to get the feed_name and feedgenerator from the url.

    e.g.:
    >>> from pprint import pprint
    >>> f = FeedFormat()
    >>> f.parse_filename(".../FooBar/feed.rss")
    >>> pprint(f)
    {'feed_name': 'feed',
     'feed_type': 'rss',
     'filename': 'feed.rss',
     'format_info': {'ext': u'rss',
                     'generator': <class 'django.utils.feedgenerator.Rss201rev2Feed'>,
                     'info_link': u'http://en.wikipedia.org/wiki/RSS',
                     'title': u'RSS v2.01rev2 (Really Simple Syndication)'},
     'raw_ext': '.rss',
     'raw_filename': '.../FooBar/feed.rss'}
    """
    def parse_filename(self, raw_filename):
        """
        returns feed_name and django.utils.feedgenerator based on the given url
        """
        self["raw_filename"] = raw_filename
        self["filename"] = os.path.basename(raw_filename)
        self["feed_name"], self["raw_ext"] = os.path.splitext(self["filename"])

        self["feed_type"] = self["raw_ext"].lstrip(".").lower()
        self["format_info"] = FORMAT_INFO_DICT[self["feed_type"]]


class FeedInfo(dict):
    """
    One syndication feed
    """
    def __init__(self, url, title_info, filename):
        self["url"] = url
        self["title_info"] = title_info
        self["filename"] = filename



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."