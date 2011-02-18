# coding: utf-8

"""
    PyLucid markup content form widget
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.forms.widgets import Textarea, Select
from django.template.loader import render_to_string


class MarkupContentWidget(Textarea):
    def render(self, name, value, attrs=None):
        form_field_html = super(MarkupContentWidget, self).render(name, value, attrs)
        context = {
            "form_field_html": form_field_html,
            "field_id": attrs['id'],
        }
        return render_to_string("pylucid/markup/content_widget.html", context)


class MarkupSelectWidget(Select):
    def render(self, name, value, attrs=None):
        form_field_html = super(MarkupSelectWidget, self).render(name, value, attrs)
        context = {
            "form_field_html": form_field_html,
            "field_id": attrs['id'],
        }
        return render_to_string("pylucid/markup/select_widget.html", context)
