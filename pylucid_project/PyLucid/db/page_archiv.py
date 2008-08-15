# -*- coding: utf-8 -*-
"""
    PyLucid cms page archiv
    ~~~~~~~~~~~~~~~~~~~~~~~

    some shared functions around the cms page archiv.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from PyLucid.models import Page, PageArchiv

# All common field names of the two models 'Page' and 'PageArchiv'
SHARING_FIELDS = (
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
    for fieldname in SHARING_FIELDS:
        field_value = getattr(page_instance, fieldname)
        setattr(archiv_entry, fieldname, field_value)

    # set ForeignKey to the original page
    archiv_entry.page = page_instance

    archiv_entry.edit_comment = edit_comment

    archiv_entry.save()

def get_archivelist(page):
    """
    returns a query set with a list of all page archiv objects for the
    given page.
    """
    query_set = PageArchiv.objects.all()
    query_set = query_set.filter(page=page).order_by('-lastupdatetime')
    return query_set

def get_last_archived_page(page):
    """
    Returns the last entrie in the page archive for the given page.
    """
    query_set = get_archivelist(page)
    last_archived_page = query_set[0]
    return last_archived_page

