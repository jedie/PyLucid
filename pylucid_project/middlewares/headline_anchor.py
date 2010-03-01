# -*- coding: utf-8 -*-

"""
    PyLucid headline anchor
    ~~~~~~~~~~~~~~~~~~~~~~~

    A middleware to add a human readable, url safe anchor to all html headlines.
    Every anchor is a permalink to the page. So you can easy copy&paste the
    links for several use.
    
    If the TOC plugin used -> insert a table of contents
    
    more info: http://pylucid.org/_goto/147/Headline-anchor/    

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import re

from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.conf import settings

from pylucid_project.utils.slug import makeUniqueSlug


class HeadlineAnchor(object):
    HEADLINE_RE = re.compile(r"<h(\d)>(.+?)</h(\d)>(?iusm)")

    def __init__(self, permalink):
        self.permalink = permalink
        self.toc_list = [] # Storage for self.build_toc()
        self._anchor_list = [] # For makeUniqueSlug

    def insert_links(self, content):
        assert isinstance(content, unicode), "content must be unicode!"

        # add the anchor with re.sub
        new_content = self.HEADLINE_RE.sub(self.add_anchor, content)
        return new_content

    def add_anchor(self, matchobj):
        """
        add a unique anchor to a html headline.
        """
        link_text = matchobj.group(2)
        link_text = mark_safe(link_text)

        # Strip all non-ASCII and make the anchor unique
        anchor = makeUniqueSlug(link_text, self._anchor_list)

        # Remember the current anchor.
        # So makeUnique can add a number on double anchors.
        self._anchor_list.append(anchor)

        anchor_link = self.permalink + "#" + anchor

        context = {
            "no": matchobj.group(1),
            "link_text": link_text,
            "anchor": anchor,
            "anchor_link": anchor_link,
        }

        self.toc_list.append(context) # Save for self.build_toc()

        result = render_to_string("pylucid/headline_anchor.html", context)
        return result

    def build_toc(self, toc_min_count):
        """
        Build the HTML code of the TOC
        """
        if len(self.toc_list) < toc_min_count:
            return u""

        context = {"toc_list": self.toc_list}

        result = render_to_string("TOC/TOC.html", context)
        return result


class HeadlineAnchorMiddleware(object):
    def process_response(self, request, response):
        """
        Add anchors to every html headlines.
        """
        # Put only the statistic into HTML pages
        if not "html" in response._headers["content-type"][1]:
            # No HTML Page -> do nothing
            return response

        if response.status_code != 200:
            # do nothing on e.g. permission deny or not found or redirects etc.
            return response

        try:
            # Get the permalink to the current page
            permalink = request.PYLUCID.context["page_permalink"]
        except AttributeError, KeyError:
            # We are not on a cms page -> e.g.: in the admin pandel
            # No cms page request -> do nothing
            #print "*** No request.PYLUCID.pagemeta!", response._headers["content-type"]
            permalink = request.path

        # response is a HttpResponse object. Get the content via response.content will
        # encode it to byte string, but we need unicode.
        content = force_unicode(response.content, encoding=response._charset)

        # insert the Headline links
        headline_anchor = HeadlineAnchor(permalink)
        content = headline_anchor.insert_links(content)

        if settings.PYLUCID.TOC_PLACEHOLDER in content:
            # lucidTag TOC is in the content -> insert a table of contents
            toc_min_count = request.PYLUCID._toc_min_count # Added in lucidTag TOC
            toc_html = headline_anchor.build_toc(toc_min_count)
            content = content.replace(settings.PYLUCID.TOC_PLACEHOLDER, toc_html)

        response.content = content
        return response
