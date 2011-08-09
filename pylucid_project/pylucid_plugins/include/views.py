# coding: utf-8

"""
    PyLucid include plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import traceback

from django.conf import settings
from django.contrib import messages
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.markup import MARKUP_DATA
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.markup.hightlighter import make_html
from pylucid_project.utils.escape import escape


MARKUPS = dict(tuple([(data[1], data[0]) for data in MARKUP_DATA]))


def _error(request, msg, staff_msg):
    etype, value, tb = sys.exc_info()
    if tb is not None:
#        if settings.DEBUG and settings.RUN_WITH_DEV_SERVER:
#            raise
        if request.user.is_superuser:
            # put the full traceback into page_msg, but only for superusers
            messages.debug(request,
                mark_safe(
                    "%s:<pre>%s</pre>" % (
                        staff_msg, traceback.format_exc()
                    )
                )
            )
            return

    if request.user.is_staff:
        messages.error(request, staff_msg)

    return "[%s]" % msg


def _render(request, content, path_or_url, markup, highlight, ext, strip_html):
    # XXX: markup + sript html???
    markup_no = None
    if markup:
        if markup not in MARKUPS:
            return _error(request, "Include error.",
                "Can't include: Unknown markup %r (Available: %s)" % (markup, ", ".join(MARKUPS.keys()))
            )
        markup_no = MARKUPS[markup]

    if markup_no:
        content = apply_markup(content, markup_no, request, escape_django_tags=False) # xxx: escape_django_tags
        if highlight and not ext:
            ext = "html"

    if highlight:
        if ext:
            source_type = ext
        else:
            source_type = os.path.splitext(path_or_url)[1]
        content = make_html(content, source_type)

    if not (markup_no or highlight):
        if strip_html:
            content = strip_tags(content)
        content = escape(content)

    return content


def local_file(request, filepath, encoding="utf-8", markup=None, highlight=False, ext=None, strip_html=True):
    """
    include a local files from filesystem into a page.
    Arguments, see DocString of lucidTag()
    """
    try:
        f = file(filepath, "r")
        content = f.read()
        f.close()

        content = unicode(content, encoding)
    except Exception, err:
        return _error(request, "Include error.", "Can't read file %r: %s" % (filepath, err))

    return _render(request, content, filepath, markup, highlight, ext, strip_html)


def remote(request, url, encoding="utf-8", markup=None, strip_html=True):
    raise NotImplemented("TODO!")


def lucidTag(request, **kwargs):
    """
    include a local file or a remote page into CMS page.
    
    Available arguments are:
    |= parameter |= default |= description
    | encoding   | "utf-8"  | content charset
    | markup     | None     | Name of the Markup to apply (e.g.: "creole", "rest")
    | highlight  | False    | Highlight the content with pygments?
    | ext        | None     | File extensions for pygments (e.g.: "py", "html+django")
    | strip_html | True     | Cut html tags out from content?
    
    You can combine markup and highlight. Result is pygmentised html code ;)
    if not markup and not highlight, the result would be strip_html (optional) and then escaped. 
    
    example:
    
    {% lucidTag include.local_file filepath="README.creole" markup="creole" %}
    {% lucidTag include.remote url="/foo/bar/README.creole" markup="creole" %}
    """
    return _error(request, "Include error.",
        "Wrong lucidTag Syntax:"
        " You must use {% lucidTag.local_file ... %} or {% lucidTag.remote ... %} !"
    )
