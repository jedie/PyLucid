#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    PyLucid back links Plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a horizontal backlink bar.
    Adjastuble with the following Parameters

    - print_last_page = False (default)
        if print_last_page has the value True, then the actual page will be the
        last page in the bar. Otherwise the parentpage.

    - print_index = False (default)
        display a link to the index ("/") if = True


    - index = "Index" (default)
        the name that is printed for the indexpage


    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :created: 29.11.2005 10:14:02 by Jens Diemer
    :copyleft: 2005-2008 by Jens Diemer, Manuel Herzog
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev$"


from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Page

class back_links(PyLucidBasePlugin):

    def lucidTag(self, print_last_page=False, print_index=False, index="Index"):
        """
        generate the backlinks
        """
        current_page = self.context["PAGE"]
        if print_last_page == True:
            print_page = current_page
        else:
            print_page = current_page.parent
            if not print_page:
                # There exist no higher-ranking page
                return ""

        data = self.backlink_data(print_page)
        data.reverse()

        context = {
            "pages": data,
            "print_index": print_index,
            "index": index,
        }
        self._render_template("back_links", context)#, debug=True)

    def backlink_data(self, parent_page):
        """
        make a list of all pages in the current way back to the index page.
        """
        data = []
        while parent_page:
            page_id = parent_page.id
            page = Page.objects.get(id=page_id)
            parent_page = page.parent

            data.append(page)

        return data

