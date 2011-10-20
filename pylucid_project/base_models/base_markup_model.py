# coding: utf-8

"""
    PyLucid base models
    ~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import models
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.template import render
from django_tools.middlewares.ThreadLocal import get_current_request

from pylucid_project.apps.pylucid.fields import MarkupModelField, \
    MarkupContentModelField
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.markup.django_tags import DjangoTagAssembler



class MarkupBaseModel(models.Model):
    """
    For models with content + markup field
    """
    content = MarkupContentModelField(
        _('Content'), blank=True, help_text=_("raw markup content.")
    )
    markup = MarkupModelField(
        _('Markup'), help_text=_("Specifiy the used content markup.")
    )

    def get_html(self, request=None, escape_django_tags=False, render_django_tags=False):
        """
        return self.content rendered as html:
            1. apply markup
            2. parse lucidTags/django template tags
        """
        if request is None:
            # e.g. called from template
            request = get_current_request()

        content1 = apply_markup(self.content, self.markup, request, escape_django_tags=escape_django_tags)

        if not render_django_tags:
            return content1
        else:
            context = request.PYLUCID.context
            content2 = render.render_string_template(content1, context)
            return content2

    def get_search_content(self, request):
        """
        Use this content for display search results:
        * render markup content to html without existing django tags
        """
        content = self.get_html(request)

        # remove django tags
        assembler = DjangoTagAssembler()
        content2, cut_data = assembler.cut_out(content)

        return content2

    class Meta:
        abstract = True
