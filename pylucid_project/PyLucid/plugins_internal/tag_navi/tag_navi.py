# -*- coding: utf-8 -*-

"""
    PyLucid tag navigation
    ~~~~~~~~~~~~~~~~~~~~~~
    
    A tag based navigation throu the cms pages.
    
    TODO: At the moment we used the keyword field here, but this should be
        changed to a real tagging 

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev:$"

import urllib

from PyLucid.models import Page
from PyLucid.system.BasePlugin import PyLucidBasePlugin


class tag_navi(PyLucidBasePlugin):
    def lucidTag(self):
        """
        insert the tag link list into the cms page.
        """
        keywords = self.current_page.keywords
        
        tags = []
        for tag in keywords.split(","):
            tag = tag.strip()
            tags.append({
                "name": tag,
                "url": self.URLs.methodLink("page_list", tag),
            })

        context = {
            "tags": tags,
        }
        self._render_template("tag_links", context)#, debug=2)
        
    def page_list(self, tag=None):
        """
        Display all pages tagged with the given >tag<.
        """
        if not tag:
            self.page_msg.red("Wrong URL!")
            return
        
        try:
            tag = urllib.unquote_plus(tag.strip("/"))
        except Exception:
            if self.request.debug:
                raise
            else:
                self.page_msg.red("Wrong URL!")
                return
               
        pages = Page.objects.all().filter(showlinks = True)
        if self.request.user.is_anonymous():
            pages = pages.exclude(permitViewPublic = False)

        pages = pages.filter(keywords__icontains=tag)
        
        context = {
            "selected_tag": tag,
            "pages": pages,
        }
        self._render_template("select_page", context)#, debug=2)