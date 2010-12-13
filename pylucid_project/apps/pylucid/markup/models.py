# coding: utf-8

"""
    PyLucid markup content base model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models

from django_tools.utils.messages import failsafe_message

from pylucid_project.apps.pylucid.fields import MarkupModelField
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.markup.widgets import MarkupContentWidget


class MarkupContentModelField(models.TextField):
    """
    A model field for a django-tagging field.
    Use a own widget to display existing tags and make them clickable with jQuery. 
    """
    def formfield(self, **kwargs):
        # Use our own widget and give him access to the model class
        kwargs['widget'] = MarkupContentWidget()
        return super(MarkupContentModelField, self).formfield(**kwargs)


class MarkupBaseModel(models.Model):
    content = MarkupContentModelField()
    markup = MarkupModelField()

    def get_html(self):
        """ returns the generate html content. """
        return apply_markup(self.content, self.markup, failsafe_message)

    class Meta:
        abstract = True
