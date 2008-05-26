#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    PyLucid.db.page
    ~~~~~~~~~~~~~~~

    some needfull functions around the cms page navigation tree.

    TODO: This stuff shoud be went into ./PyLucid/models/Page.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

#TODO: We need a caching for:
#      page-ID  <-> parant-ID relation?
#      url data for every page?

from django import newforms as forms
from django.newforms.util import ValidationError
from django.utils.translation import ugettext as _

from PyLucid.models import Page
from PyLucid.tools.tree_generator import TreeGenerator

def get_update_info(context, count=10):
    """
    get the last >count< page updates.
    Used by page_update_list and the RSSfeedGenerator
    """
    pages = Page.objects.order_by('-lastupdatetime')
    pages = pages.filter(showlinks = True)

    request = context["request"]
    if request.user.is_anonymous():
        pages = pages.exclude(permitViewPublic = False)

    pages = pages[:count]

    # Add the attribute 'absolute_uri' to every page:
    for page in pages:
        location = page.get_absolute_url()
        absolute_uri = request.build_absolute_uri(location)
        page.absolute_uri = absolute_uri

    return pages


def flat_tree_list(generate_level_names=True):
    """
    Generate a flat page list.
    Usefull for a html select input, like this:
        <option value="1">___| about</option>
        <option value="2">______| features</option>
        <option value="3">_________| unicode</option>
        <option value="4">_________| unicode test</option>
        <option value="5">______| news</option>
        <option value="6">_________| SVN news</option>
    """
    page_data = Page.objects.values(
        "id", "parent", "name", "title", "shortcut"
    ).order_by("position", "name", "id")
    tree = TreeGenerator(page_data)
    tree.activate_all()
    page_list = tree.get_flat_list()

    if generate_level_names:
        for page in page_list:
            page["level_name"] = " %s| %s" % (
                "_"*((page["level"]*2)-2), page["name"]
            )

    return page_list


#______________________________________________________________________________
# Data access for main-/sub-menu and sitemap:


def _get_page_data(request):
    """
    shared function for get_sitemap_tree() and get_main_menu_tree()
    """
    page_data = Page.objects.values(
        "id", "parent", "name", "title", "shortcut"
    ).filter(showlinks = True).order_by("position", "name", "id")

    if request.user.is_anonymous():
        page_data = page_data.exclude(permitViewPublic = False)

    return page_data


def get_sitemap_tree(request):
    """
    Generate a tree of all pages for the sitemap.
    """
    # Get all pages from the database:
    sitemap_data = _get_page_data(request)
    tree = TreeGenerator(sitemap_data)
    sitemap_tree = tree.get_sitemap_tree()
    return sitemap_tree


def get_main_menu_tree(request, current_page_id):
    """
    Generate a opened tree dict for the given >current_page_id<.
    """
    # Get all pages from the database:
    menu_data = _get_page_data(request)
    # Build the tree:
    tree = TreeGenerator(menu_data)
    # Generate the opened tree dict:
    menu_data = tree.get_menu_tree(current_page_id)
    return menu_data


def get_sub_menu_data(request, current_page_id):
    """
    returned a list of all sub pages for the >current_page_id<.
    """
    sub_pages = Page.objects.all().filter(
        parent = current_page_id, showlinks = True
    ).order_by("position", "name", "id")

    if request.user.is_anonymous():
        sub_pages = sub_pages.exclude(permitViewPublic = False)

    return sub_pages

#______________________________________________________________________________
# newforms Page choice
"""
# usage:

from PyLucid.db.page import PageChoiceField, get_page_choices
class MyForm(forms.Form):
    ...
    page = PageChoiceField(widget=forms.Select(choices=get_page_choices()))
    ...
"""

class PageChoiceField(forms.IntegerField):
    def clean(self, page_id):
        """
        returns the parent page instance.
        Note:
            In PyLucid.models.Page.save() it would be checkt if the selected
            parent page is logical valid. Here we check only, if the page with
            the given ID exists.
        """
        if page_id == None:
            # assigned to tree root
            return None

        # let convert the string into a integer:
        page_id = super(PageChoiceField, self).clean(page_id)

        if page_id == 0:
            # assigned to the tree root.
            return None

        try:
            #page_id = 999999999 # Not exists test
            page = Page.objects.get(id=page_id)
        except Exception, msg:
            raise ValidationError(_(u"Wrong parent POST data: %s" % msg))
        else:
            return page_id


def get_page_choices():
    """
    generate a verbose page name tree for the parent choice field.
    """
    page_list = flat_tree_list()
    choices = [(0, "---[root]---")]
    for page in page_list:
        choices.append((page["id"], page["level_name"]))
    return choices
