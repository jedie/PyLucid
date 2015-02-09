# coding: utf-8


"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.models import UpdateInfoBaseModel
from django_tools.template import render


class EditableHtmlHeadFile(UpdateInfoBaseModel):
    """
    Storage for editable static text files, e.g.: stylesheet / javascript.

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    filepath = models.CharField(max_length=255, unique=True)
    mimetype = models.CharField(max_length=64,
        help_text=_("MIME type for this file. (Leave empty for guess by filename)")
    )
    html_attributes = models.CharField(max_length=256, null=False, blank=True,
        help_text=_('Additional html tag attributes (CSS example: media="screen")')
    )
    render = models.BooleanField(default=False,
        help_text=_("Are there CSS ColorScheme entries in the content?")
    )
    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    def get_rendered(self, colorscheme):
        color_dict = colorscheme.get_color_dict()

        for name, value in color_dict.items():
            color_dict[name] = "#%s" % value

        rendered_content = render.render_string_template(self.content, color_dict)
        return rendered_content

    def __unicode__(self):
        return self.filepath

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'pylucid_editablehtmlheadfile'
        ordering = ("filepath",)




