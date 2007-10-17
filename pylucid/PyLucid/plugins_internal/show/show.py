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
from PyLucid.tools.content_processors import apply_markup, escape_django_tags


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

    def menu(self):
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

    def all_pages(self):
        current_page = self.context["PAGE"]
        current_page.title = "all pages"
        current_page_id = current_page.id

#        page_data = Page.objects.values(
#            "id", "parent", "shortcut", "name", "title",
#            "template", "content", "markup"
#        ).order_by("position")

        pages = Page.objects.all().order_by("position")
        page_data = []
        for page in pages:
            content = escape_django_tags(page.content)
            parent = getattr(page.parent, "id", None)
            url = page.get_absolute_url()

            page_data.append({
                "id": page.id,
                "parent": parent,
                "shortcut": page.shortcut,
                "name": page.name,
                "title": page.title,
                "content": content,
                "template": page.template.id,
                "markup": page.markup,
                "url": url,
            })
#        self.page_msg(page_data)

        tree = TreeGenerator(page_data)
        page_list = tree.get_group_list(
            group_key="template", id=current_page_id
        )[1:]
        for page in page_list:
            content = page["content"]
            markup_object = page["markup"]
            content = apply_markup(content, self.context, markup_object)
            page["content"] = content
#        self.page_msg(page_list)

        context = {
            "page_list": page_list,
        }
        self._render_template("all_pages", context)#, debug=True)



