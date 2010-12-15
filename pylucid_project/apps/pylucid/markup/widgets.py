# coding: utf-8

"""
    PyLucid markup content form widget
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.forms.widgets import Textarea
from django.template.loader import render_to_string

class MarkupContentWidget(Textarea):
    def render(self, name, value, attrs=None):
        form_field_html = super(MarkupContentWidget, self).render(name, value, attrs)
        context = {
            "form_field_html": form_field_html,
            "field_id": attrs['id'],
            "id_prefix": attrs['id'].split("-")[0] # FIXME: How to get the form prefix here?
        }
        return render_to_string("pylucid/markup/content_widget.html", context)
