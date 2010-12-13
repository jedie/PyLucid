# coding: utf-8

"""
    PyLucid markup ajax preview view
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.http import HttpResponse

from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.markup.forms import MarkupPreviewForm


def markup_preview(request):
    """
    markup preview AJAX view.
    """
    if not request.user.is_authenticated():
        raise PermissionDenied()

    if not request.is_ajax() or request.method != 'POST':
        raise SuspiciousOperation()

    form = MarkupPreviewForm(request.POST)
    if not form.is_valid():
        return HttpResponse("Error: Form not valid: %r" % form.errors)

    content = form.cleaned_data["content"]
    markup = form.cleaned_data["markup"]

    html = apply_markup(content, markup, request, escape_django_tags=True)

    return HttpResponse(html)



