# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~
    
    TODO: move this model to i18n app!

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib.auth.models import Group
from django.db import models

from django_tools.models import UpdateInfoBaseModel

from pylucid_migration.base_models.many2many import AutoSiteM2M



class Language(AutoSiteM2M, UpdateInfoBaseModel):
    """
    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
        
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    code = models.CharField(unique=True, max_length=10)
    description = models.CharField(max_length=150, blank=True,
        help_text="Description of the Language (filled automaticly)"
    )

    permitViewGroup = models.ForeignKey(Group, related_name="%(class)s_permitViewGroup",
        help_text="Limit viewable to a group for a complete language section?",
        null=True, blank=True,
    )

    def __unicode__(self):
        return u"Language %s - %s" % (self.code, self.description)

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'pylucid_language'
        ordering = ("code",)
