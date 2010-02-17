# coding: utf-8

"""
    Get and replace headlines with anchors.
    Used in:
     - pylucid_project.middlewares.headline_anchor.HeadlineAnchorMiddleware
     - pylucid_project.pylucid_plugins.TOC

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import re

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from pylucid_project.utils.slug import makeUniqueSlug



class HeadlineAnchor(object):
    HEADLINE_RE = re.compile(r"<h(\d)>(.+?)</h(\d)>(?iusm)")

    def __init__(self, permalink, callback=None):
        self.permalink = permalink
        self.callback = callback
        self.anchor_list = []

    def insert_links(self, content):
        assert isinstance(content, unicode), "content must be unicode!"

        # add the anchor with re.sub
        new_content = self.HEADLINE_RE.sub(self.add_anchor, content)
        return new_content

    def add_anchor(self, matchobj):
        """
        add a unique anchor to a html headline.
        """
        txt = matchobj.group(2)
        txt = mark_safe(txt)

        # Strip all non-ASCII and make the anchor unique
        anchor = makeUniqueSlug(txt, self.anchor_list)

        # Remember the current anchor. So makeUnique can add a number on double
        # anchors.
        self.anchor_list.append(anchor)

        anchor_link = self.permalink + "#" + anchor

        context = {
            "no": matchobj.group(1),
            "txt": txt,
            "anchor": anchor,
            "anchor_link": anchor_link,
        }
        result = render_to_string("pylucid/headline_anchor.html", context)

        if self.callback:
            self.callback(matchobj, result, anchor, anchor_link)
        return result
