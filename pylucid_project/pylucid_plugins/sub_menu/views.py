# -*- coding: utf-8 -*-

"""
    PyLucid sub_menu plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a link list of all sub pages.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2005-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev$"


from pylucid.models import PageMeta
from pylucid.decorators import render_to


@render_to("sub_menu/sub_menu.html")
def lucidTag(request):
    """
    build the sub menu with all existing sub pages
    TODO: filter showlinks and permit settings
    TODO: sort by PageTree position!
    """
    # Get the current models.PageContent instance
    pagetree = request.PYLUCID.pagetree
    current_lang = request.PYLUCID.language_entry

    sub_pages = PageMeta.objects.all().filter(page__parent=pagetree, lang=current_lang)

    return {"sub_pages": sub_pages}











