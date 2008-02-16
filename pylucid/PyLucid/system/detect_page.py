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

from PyLucid.models import Page, Preference, Template
from PyLucid.system.exceptions import AccessDenied

from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404

def get_a_page():
    """
    Try to get and return a existing page.
    Create a first page, if no page exists.
    """
    try:
        return Page.objects.all().order_by("parent", "position")[0]
    except Exception, e:
        # FIXME: Normaly we should use the exception type "Page.DoesNotExist"
        #    but this doesn't work, why?
        msg = (
            "Error getting a cms page content."
            " - (Have you installed PyLucid currectly?)"
            " - Original Error was: '%s'"
        ) % e
        raise ImproperlyConfigured(msg)


def get_default_page_id():
    """
    returns the default page id
    """
    try:
        default_page = Preference.objects.get(name__exact="index page")
#        default_page = "raise!"
        return int(default_page.value)
    except Exception, e:
        # TODO: make a page message for the admin
        # Get the first page
        return get_a_page().id

def get_default_page(request):
    page_id = get_default_page_id()
    try:
#        page_id = "wrong test"
        return Page.objects.get(id__exact=page_id)
    except Exception, e:
        # The defaultPage-ID from the Preferences is wrong!
        return get_a_page()


def get_current_page_obj(request, url_info):
    """
    returns the page object
    use:
     - the shortcut in the requested url
    or:
     - the default page (stored in the Preference table)
    """
    # /bsp/und%2Foder/ -> bsp/und%2Foder
    page_name = url_info.strip("/")

    if page_name == "":
        # Index Seite wurde aufgerufen. Zumindest bei poor-modrewrite
        return get_default_page(request)

    # bsp/und%2Foder -> ['bsp', 'und%2Foder']
    shortcuts = page_name.split("/")

    shortcuts.reverse()
    wrong_shutcuts = []
    # FIXME: We need no for loop here, isn't it?
    for shortcut in shortcuts:
        try:
            page = Page.objects.get(shortcut__exact=shortcut)
        except Page.DoesNotExist:
            raise Http404(_("Page '%s' doesn't exists.") % shortcut)

        if request.user.is_anonymous() and not page.permitViewPublic:
            raise AccessDenied
        else:
            return page
