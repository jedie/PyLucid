# coding: utf-8

"""
    PyLucid include plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import traceback

from django.conf import settings
from django.contrib import messages
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.markup import MARKUP_DATA
from pylucid_project.apps.pylucid.markup.converter import apply_markup


MARKUPS = dict(tuple([(data[1], data[0]) for data in MARKUP_DATA]))


def _error(request, msg, staff_msg):
#    if settings.DEBUG and settings.RUN_WITH_DEV_SERVER:
#        raise

    if request.user.is_superuser:
        # put the full traceback into page_msg, but only for superusers
        messages.debug(request, mark_safe("%s:<pre>%s</pre>" % (msg, traceback.format_exc())))
    elif request.user.is_staff:
        messages.error(request, staff_msg)
    return "[%s]" % msg


def _render(request, content, markup, strip_html):
    # XXX: markup + sript html???

    if markup:
        if markup not in MARKUPS:
            return _error(request, "Include error.",
                "Can't include: Unknown markup %r (Available: %s)" % (markup, ", ".join(MARKUPS.keys()))
            )
        markup_no = MARKUPS[markup]
        result = apply_markup(content, markup_no, request, escape_django_tags=False) # xxx: escape_django_tags
    else:
        result = strip_tags(content)

    return result


def local_file(request, filepath, encoding="utf-8", markup=None, strip_html=True):
    """

    """
    try:
        f = file(filepath, "r")
        content = f.read()
        f.close()

        content = unicode(content, encoding)
    except Exception, err:
        return _error(request, "Include error.", "Can't read file %r: %s" % (filepath, err))

    return _render(request, content, markup, strip_html)


def remote(request, url, encoding="utf-8", markup=None, strip_html=True):
    raise NotImplemented("TODO!")


def lucidTag(request):
    """
    include a local file or a remote page into CMS page.
    
    example:
    
    {% lucidTag include.local_file filepath="README.creole" markup="creole" %}
    {% lucidTag include.remote url="/foo/bar/README.creole" markup="creole" %}
    """
    pass
