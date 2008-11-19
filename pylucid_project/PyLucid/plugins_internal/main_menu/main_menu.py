# -*- coding: utf-8 -*-

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
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

__version__= "$Rev$"

from PyLucid.db.page import get_main_menu_tree
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.utils import escape
from django.utils.safestring import mark_safe



class main_menu(PyLucidBasePlugin):

    def lucidTag(self, min=1, max=0):
        """
        write the current opened tree menu
        """
        current_page = self.context["PAGE"]
        self.current_page_id  = current_page.id
        self.min = min
        self.max = max

        # Get the menu tree dict from the database:
        menu_tree = get_main_menu_tree(self.request, self.current_page_id)

        # Create from the tree dict a nested html list.
        menu_html = self.get_html(menu_tree)

        context = {
            "menu": menu_html,
            "min": min,
            "max": max
        }
        self._render_template("main_menu_ul", context)


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

            entry["href"] = "/" + href + "/"

            if (int(entry["level"]) <= self.max or self.max<self.min) and \
                                            int(entry["level"]) >= self.min:

                if entry.has_key("subitems"):
                    # go recusive deeper into the menu entries
                    entry["submenu"] = self.get_html(
                        entry["subitems"], parent=href
                    )
                else:
                    entry["submenu"] = ""

                # Add min, max set in the lucidTag method to the local context 
                entry["min"] = self.min
                entry["max"] = self.max

                # Render one menu entry
                html = self._get_rendered_template("main_menu_li", entry)
                result.append(html)
            elif int(entry["level"]) < self.min:
                if entry.has_key("subitems"):
                    html = self.get_html(entry["subitems"],parent=href)
                    result.append(html)

        if result == []:
            menu_html = ""
        else:           
            menu_html = "\n".join(result)

        return mark_safe(menu_html)
