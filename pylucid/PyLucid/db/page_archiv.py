#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
    PyLucid cms page archiv
    ~~~~~~~~~~~~~~~~~~~~~~~

    some shared functions around the cms page archiv.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from PyLucid.models import Page, PageArchiv

# All common field names of the two models 'Page' and 'PageArchiv'
SHARING_FELDS = (
    'content', 'parent', 'position', 'name', 'shortcut', 'title',
    'template', 'style', 'markup', 'keywords', 'description',
    'createtime', 'lastupdatetime', 'createby', 'lastupdateby',
    'showlinks', 'permitViewPublic', 'permitViewGroup', 'permitEditGroup',
)

def archive_page(page_instance, edit_comment):
    """
    Archive a cms page.

    Add a new item in the page archiv and transfer all shared field values from
    the given page instance to the archiv entry.
    """
    archiv_entry = PageArchiv()
    for fieldname in SHARING_FELDS:
        field_value = getattr(page_instance, fieldname)
        setattr(archiv_entry, fieldname, field_value)

    # set ForeignKey to the original page
    archiv_entry.page = page_instance

    archiv_entry.edit_comment = edit_comment

    archiv_entry.save()