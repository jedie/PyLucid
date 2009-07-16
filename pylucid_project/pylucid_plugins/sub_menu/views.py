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


from pylucid.models import PageContent
from pylucid.decorators import render_to


@render_to("sub_menu/sub_menu.html")
def lucidTag(request):
    # Get the current models.PageContent instance
    pagecontent = request.PYLUCID.pagecontent

    sub_pages = PageContent.objects.get_sub_pages(pagecontent)

    return {"sub_pages": sub_pages}











