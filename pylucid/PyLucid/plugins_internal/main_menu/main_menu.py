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
from django.utils.safestring import mark_safe



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
        menu_html = self.get_html(menu_tree)

        context = {
            "menu": menu_html,
        }
        self._render_template("main_menu", context)


    def get_html(self, menu_data, parent=None):
        """
        Generate a nested html list from the given tree dict.
        """
        result = []

        for entry in menu_data:

            # Generate the absolute url to the page:
            href = []
            if parent:
                href.append(parent)
            href.append(entry["shortcut"])
            href = "/".join(href)

            entry["href"] = "/" + href

            if entry.has_key("subitems"):
                # go recusive deeper into the menu entries
                entry["submenu"] = self.get_html(entry["subitems"], parent=href)
            else:
                entry["submenu"] = ""

            if entry["id"] == self.current_page_id:
                # Mark the last menu item, the current displayed page
                entry["is_current"] = True

            # Render one menu entry
            html = self._get_rendered_template("main menu li", entry)
            result.append(html)

        context = {
            "menu": mark_safe("\n".join(result)),
        }

        # render all menu entries into a <ul> tag
        menu_html = self._get_rendered_template("main menu ul", context)

        return mark_safe(menu_html)

