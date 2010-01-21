# coding: utf-8

"""
    PyLucid 'table of contents' plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    FIXME: A plugin can't change the PageContent on the fly. So we can't insert the
        needed anchors here. We only parse the html code, get the links and save
        if into anchor_cache.
        The HeadlineAnchorMiddleware used the cache and insert the anchor links.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev:$"

from django.conf import settings

from pylucid_project.apps.pylucid.system.sub_headline_anchor import HeadlineAnchor
from pylucid_project.apps.pylucid.decorators import render_to


class TOC(object):
    def __init__(self, permalink):
        self.permalink = permalink
        self.toc_list = []
        self.anchor_cache = []

    def build_toc(self, content):
        h = HeadlineAnchor(permalink=self.permalink, callback=self.anchor_callback)
        h.insert_links(content)

    def anchor_callback(self, matchobj, result, anchor, anchor_link):
        self.anchor_cache.append((matchobj.group(0), result))
        link_text = matchobj.group(2)
        self.toc_list.append({
            "link_text": link_text,
            "anchor": anchor,
        })


@render_to("TOC/TOC.html")
def lucidTag(request, min=3):
    """
    Table of contents
    
    Built a list of all headlines.
    Can be inserted into PageContent or into global template.
    
    TOC is displayed only if there exists at least the
    specified number of headings. (lucidTag parameter 'min')
    
    example:
        {% lucidTag TOC %}
        {% lucidTag TOC min=4 %}
    """
    try:
        min = int(min)
    except Exception, err:
        if settings.DEBUG or request.user.is_staff:
            request.page_msg.error(
                _("'min' parameter in lucidTag TOC must be a integer! Error: %s") % err
            )
        min = 3

    pagemeta = request.PYLUCID.pagemeta
    # Get the permalink to the current page
    permalink = pagemeta.get_permalink()

    # Get the current page content
    context = request.PYLUCID.context
    try:
        raw_html_content = context["page_content"]
    except KeyError, err:
        # FIXME: The plugin can't get the page content here.
        # This allays appears, if the current page is a PluginPage and the plugin generate the 
        # complete page by extents the global template.
        if settings.DEBUG or request.user.is_superuser:
            request.page_msg("Error inserting TOC: Can't get content: %s" % err)
        return

    t = TOC(permalink)
    t.build_toc(raw_html_content)

    toc_list = t.toc_list
    request.PYLUCID.context["anchor_cache"] = t.anchor_cache

    if len(toc_list) < min:
        return

    context = {"toc_list": toc_list}

    return context
