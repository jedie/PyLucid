#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid main menu plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a nested tree menu.

    TODO:
        - Use the django template engine to generate the nested html list from
            the tree dict. But the Problem is: There is no recusive function
            available. So we must implement this. See:

    Links about a recusive function with the django template engine:
    - http://www.python-forum.de/topic-9655.html
    - http://groups.google.com/group/django-users/browse_thread/thread/3bd2812a3d0f7700/14f61279e0e9fd90

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev$
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

__version__= "$Rev$"

from PyLucid.db.page import get_main_menu_tree
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.utils import escape


class main_menu(PyLucidBasePlugin):

    def lucidTag(self):
        """
        write the current opened tree menu
        """
        current_page = self.context["PAGE"]
        self.current_page_id  = current_page.id

        # Get the menu tree dict from the database:
        menu_tree = get_main_menu_tree(self.request, self.current_page_id)

        # Create from the tree dict a nested html list.
        menu_data = self.get_html(menu_tree)

        self.response.write(menu_data)


    def get_html(self, menu_data, parent=None):
        """
        Generate a nested html list from the given tree dict.
        """
        html = (
            '<li>'
            '<a href="%(href)s" title="%(title)s">%(name)s</a>'
            '</li>'
        )
        result = ["<ul>"]

        for entry in menu_data:
            href = []
            if parent:
                href.append(parent)

            href.append(entry["shortcut"])
            href = "/".join(href)

            entry["href"] = "".join((self.URLs["absoluteIndex"], href))
            entry["name"] = escape(entry["name"])
            entry["title"] = escape(entry["title"])

            if entry["id"] == self.current_page_id:
                entry["name"] = (
                    '<span class="current">%s</span>'
                ) % entry["name"]

            result.append(html % entry)

            if entry.has_key("subitems"):
                result.append(
                    self.get_html(entry["subitems"], parent=href)
                )

        result.append("</ul>")
        return "\n".join(result)

