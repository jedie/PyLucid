# coding: utf-8

"""
    PyLucid utils for markup content in django forms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django import forms
from django.core.exceptions import SuspiciousOperation
from django.forms.widgets import Textarea
from django.http import HttpResponse
from django.template.loader import render_to_string

from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.models.pagecontent import PageContent


class MarkupPreviewForm(forms.ModelForm):
    class Meta:
        model = PageContent
        fields = ('content', 'markup')

class MarkupPreview(object):
    def ajax_preview(self, request, object_id):
        if not request.is_ajax() or request.method != 'POST':
            raise SuspiciousOperation()

        form = MarkupPreviewForm(request.POST)
        if not form.is_valid():
            return HttpResponse("Error: Form not valid: %r" % form.errors)

        content = form.cleaned_data["content"]
        markup = form.cleaned_data["markup"]

        html = apply_markup(content, markup, request, escape_django_tags=True)

        return HttpResponse(html)


class MarkupContentWidget(Textarea):
    def render(self, name, value, attrs=None):
        form_field_html = super(MarkupContentWidget, self).render(name, value, attrs)
        context = {
            "form_field_html": form_field_html,
            "field_id": attrs['id'],
        }
        return render_to_string("pylucid/markup/content_widget.html", context)
