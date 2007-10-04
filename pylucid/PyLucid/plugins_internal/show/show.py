#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid presentation plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Some usefull things to make PyLucid a little to Powerpoint...

    - Special back and forth navigation
    - Special menu

    TODO:
        The menu must change (must be simpler)

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

__version__= "$Rev: 1168 $"

from PyLucid.models import Page
from PyLucid.db.page import get_main_menu_tree, flat_tree_list
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.tree_generator import TreeGenerator
from PyLucid.models import Page


class show(PyLucidBasePlugin):

    def _get_pages(self):
        current_page = self.context["PAGE"]
        current_page_id = current_page.id

        tree_list = flat_tree_list(generate_level_names=False)

        backward_data = None
        forward_data = None
        for idx, page in enumerate(tree_list):
            if page["id"] == current_page_id:
                try:
                    backward_data = tree_list[idx-1]
                except IndexError:
                    # No previous page exists
                    pass
                try:
                    forward_data = tree_list[idx+1]
                except IndexError:
                    # No next page exists
                    pass

        def get_page_obj(page_data):
            """ Returns the model object, if available """
            if not page_data:
                # No back/forth page available
                return None
            page_id = page_data["id"]
            page = Page.objects.get(id__exact=page_id)
            if page.template == current_page.template:
                # The Links should only navigate inside a presentation and
                # not to a other page content (with a other template/style)
                return page
            else:
                return None

        forward_page = get_page_obj(forward_data)
        backward_page = get_page_obj(backward_data)

        return backward_page, current_page, forward_page

    def lucidTag(self):
        """
        Build the back and forth links.

        These navigation is a little special, but good for a presentation.

        back:
            Navigate to the previous page in the flat_tree_list.
        forth:
            Navigate to the next page in the flat_tree_list.

        Rule for both directions:
            - The Link is only available if the back/forth page hat the same
            template (So you can't get out of the presentation pages with this
            navigation).
            - We use the flat tree _list_, so the tree structure is not directly
            relevant.
        """
        backward_page, current_page, forward_page = self._get_pages()

        sitemap_link = self.URLs.commandLink("SiteMap", "lucidTag")

        context = {
            "backward_page": backward_page,
            "current_page": current_page,
            "forward_page": forward_page,
            "sitemap_link": sitemap_link,
        }
        self._render_template("nav_links", context)

    #__________________________________________________________________________

    def menu(self):
        """
        write the current opened tree menu
        """
        backward_page, current_page, forward_page = self._get_pages()




        current_page = self.context["PAGE"]
        self.current_page_id  = current_page.id

        # Get the menu tree dict from the database:
        menu_tree = get_main_menu_tree(self.request, self.current_page_id)

#        self.page_msg(menu_tree)

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
        if parent == None:
            result = ['<ul id="main_menu">']
        else:
            result = ["<ul>"]

        for entry in menu_data:
            href = []
            if parent:
                href.append(parent)

            href.append(entry["shortcut"])
            href = "/".join(href)

            entry["href"] = "".join((self.URLs["absoluteIndex"], href))

            if entry["id"] == self.current_page_id:
                entry["name"] = '<span class="current">%s</span>' % entry["name"]

            result.append(html % entry)

            if entry.has_key("subitems"):
                result.append(
                    self.get_html(entry["subitems"], parent=href)
                )

        result.append("</ul>")
        return "\n".join(result)

