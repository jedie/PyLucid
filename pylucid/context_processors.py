# coding: utf-8

"""
    PyLucid context processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.utils.safestring import mark_safe

from . import VERSION_STRING


def pylucid(request):
    """
    A django TEMPLATE_CONTEXT_PROCESSORS
    """
    context = {
        "powered_by": mark_safe('<a href="http://www.pylucid.org">PyLucid v%s</a>' % VERSION_STRING),
    }
    return context
