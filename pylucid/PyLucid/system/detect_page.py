#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid
    ~~~~~

    TODO: Big TODO: rewrite all. Put this into ./PyLucid/db/page.py !!!!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.utils.translation import ugettext as _
from django.http import Http404, HttpResponseRedirect

from PyLucid.system.exceptions import AccessDenied, LowLevelError
from PyLucid.models import Page, Plugin


def get_a_page():
    """
    Try to get and return a existing page.
    """
    try:
        return Page.objects.all().order_by("parent", "position")[0]
    except Exception, e:
        # FIXME: Normaly we should use the exception type "Page.DoesNotExist"
        #    but this doesn't work, why?
        msg = _("Error getting a cms page.")
        raise LowLevelError(msg, e)


def get_default_page(request):
    try:
        preferences = Plugin.objects.get_preferences("system_settings")
        page_id = preferences["index_page"]
#        page_id = "wrong test"
        return Page.objects.get(id__exact=page_id)
    except Exception, e:
        # The defaultPage-ID from the Preferences is wrong!
        return get_a_page()


def get_current_page_obj(request, url_info):
    """
    returns the page object
    -If url_info contains no shortcut -> return the default page (stored in the
        Preference table)
    -If a part of the url is wrong -> Redirect to the last right shortcut
    -if a anonymous user would get a permitViewPublic page -> raise AccessDenied
    """
    # /bsp/und%2Foder/ -> bsp/und%2Foder
    page_name = url_info.strip("/")

    if page_name == "":
        # Index Seite wurde aufgerufen. Zumindest bei poor-modrewrite
        return get_default_page(request)

    # bsp/und%2Foder -> ['bsp', 'und%2Foder']
    shortcuts = page_name.split("/")
    shortcuts.reverse()
    wrong_shortcut = False
    for shortcut in shortcuts:
        try:
            page = Page.objects.get(shortcut__exact=shortcut)
        except Page.DoesNotExist:
            wrong_shortcut = True
            continue

        if request.user.is_anonymous() and not page.permitViewPublic:
            # the page is not viewale for anonymous user
            raise AccessDenied

        # Found a existing, viewable page
        if wrong_shortcut:
            # One of the shortcuts are wrong in the url -> redirect
            return HttpResponseRedirect(page.get_absolute_url())

        return page

    # No right page found
    raise Http404(_("Page '%s' doesn't exists.") % shortcut)
