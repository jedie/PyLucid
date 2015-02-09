# coding: utf-8


"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import IntegrityError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django_tools.utils.messages import failsafe_message
from django_tools.models import UpdateInfoBaseModel


class ColorScheme(UpdateInfoBaseModel):
    """
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    name = models.CharField(max_length=255, help_text="The name of this color scheme.")

    def get_color_dict(self):
        queryset = Color.objects.filter(colorscheme=self)
        color_list = queryset.values_list('name', 'value')
        return dict(color_list)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'pylucid_colorscheme'



class Color(UpdateInfoBaseModel):
    """
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    colorscheme = models.ForeignKey(ColorScheme)
    name = models.CharField(max_length=128,
        help_text="Name if this color (e.g. main_color, head_background)"
    )
    value = models.CharField(max_length=18)

    def __unicode__(self):
        return u"Color '%s' #%s (%s)" % (self.name, self.value, self.colorscheme)

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'pylucid_color'
        unique_together = (("colorscheme", "name"),)
        ordering = ("colorscheme", "name")


