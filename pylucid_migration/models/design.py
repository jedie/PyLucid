# coding: utf-8


"""
    PyLucid Design model
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_tools.models import UpdateInfoBaseModel

from pylucid_migration.base_models.many2many import SiteM2M

# other PyLucid models
from pylucid_migration.models.colorscheme import ColorScheme


class Design(SiteM2M, UpdateInfoBaseModel):
    """
    Page design: template + CSS/JS files 

    inherited attributes from SiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    name = models.CharField(unique=True, max_length=150, help_text=_("Name of this design combination"),)
    template = models.CharField(max_length=128, help_text="filename of the used template for this page")
    headfiles = models.ManyToManyField("pylucid_migration.EditableHtmlHeadFile", null=True, blank=True,
        help_text=_("Static files (stylesheet/javascript) for this page, included in html head via link tag")
    )
    colorscheme = models.ForeignKey(ColorScheme, null=True, blank=True)

    def __unicode__(self):
        sites = self.sites.values_list('name', flat=True)
        return u"Page design '%s' (on sites: %r)" % (self.name, sites)
    __repr__ = __unicode__

    class Meta:
        db_table = u'pylucid_design'
        app_label = u'pylucid_migration'
        ordering = ("template",)
