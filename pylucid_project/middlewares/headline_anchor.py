# -*- coding: utf-8 -*-

"""
    PyLucid headline anchor
    ~~~~~~~~~~~~~~~~~~~~~~~

    A middleware to add a human readable, url safe anchor to all html headlines.
    Every anchor is a permalink to the page. So you can easy copy&paste the
    links for several use.
    
    more info: http://pylucid.org/_goto/147/Headline-anchor/    

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.utils.encoding import force_unicode

from pylucid_project.apps.pylucid.system.sub_headline_anchor import HeadlineAnchor


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
            pagemeta = request.PYLUCID.pagemeta
            context = request.PYLUCID.context
        except AttributeError:
            # No cms page request -> do nothing
            #print "*** No request.PYLUCID.pagemeta!", response._headers["content-type"]
            return response

        # response is a HttpResponse object. Get the content via response.content will
        # encode it to byte string, but we need unicode.
        content = force_unicode(response.content, encoding=response._charset)

        if "anchor_cache" in context:
            # lucidTag TOC was called in this request. The plugin has collect all
            # headlines and has build all links. We must only replace it, because
            # a lucidTag plugin can't do this!
            anchor_cache = request.PYLUCID.context["anchor_cache"]
            for orig_headline, anchor_headline in anchor_cache:
                content = content.replace(orig_headline, anchor_headline)
        else:
            # Use pylucid_project.utils.html.HeadlineAnchor for inserting
            # anchors for all existing headlines

            # Get the permalink to the current page
            permalink = pagemeta.get_permalink()

            h = HeadlineAnchor(permalink)
            content = h.insert_links(content)

        response.content = content

        return response
