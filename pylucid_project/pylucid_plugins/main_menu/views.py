# -*- coding: utf-8 -*-

"""
    PyLucid sub_menu plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a link list of all sub pages.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: 2009-04-29 14:36:54 +0200 (Mi, 29. Apr 2009) $
    $Rev: 1934 $
    $Author: JensDiemer $

    :copyleft: 2005-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev: 1934 $"

from django.template import RequestContext
from django.shortcuts import render_to_response

from pylucid.models import PageContent
from pylucid.decorators import render_to


@render_to("main_menu/main_menu.html")
def lucidTag(request):
    try:
        # Get the current models.PageContent instance
        pagecontent = request.PYLUCID.pagecontent
    except AttributeError:
        # Plugin page???
        return

#    request.page_msg(request.path)
    if request.path == "/":
        sub_pages = PageContent.objects.all().filter(page__parent=None, lang=pagecontent.lang)
    else:
        sub_pages = PageContent.objects.get_sub_pages(pagecontent)

    return {"sub_pages": sub_pages}










