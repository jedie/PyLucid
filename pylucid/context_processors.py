# coding: utf-8

"""
    PyLucid context processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.utils.safestring import mark_safe

from pylucid.version import safe_version


def pylucid(request):
    """
    A django TEMPLATE_CONTEXT_PROCESSORS
    """
    context = {
        "pylucid_version": "v%s" % safe_version,
        "powered_by": mark_safe('<a href="http://www.pylucid.org">PyLucid v%s</a>' % safe_version),
    }
    return context
