#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid back links Plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a horizontal backlink bar.
    Adjastuble with the following Parameters
      - print_last_page = False (default)
        if print_last_page has the value True, then the actual page will be the
        last page in the bar. Otherwise the parentpage.
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
from PyLucid.models import Page, Preference
from PyLucid.tools.utils import escape
from django.utils.safestring import mark_safe

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

        data = self.backlink_data(print_page, print_index)
        data.reverse()

        context = {
            "pages": data,
            "print_index": print_index,
            "index": index,
        }
        self._render_template("back_links", context)#, debug=True)

    def backlink_data(self, parent_page, print_index):
        """
        get the link data from the db
        """
        data = []
        urls = [""]


        while parent_page:
            page_id = parent_page.id
            page = Page.objects.get(id=page_id)
            parent_page = page.parent

#            if print_index == False and page_id == indexid:
#                # Don't display the default index page
#                continue

            data.append(page)

        return data

