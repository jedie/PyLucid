# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models

from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, AutoSiteM2M
from pylucid_project.pylucid_plugins import update_journal

# other PyLucid models
from colorscheme import ColorScheme


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class DesignManager(models.Manager):
    pass

class Design(AutoSiteM2M, UpdateInfoBaseModel):
    """
    Page design: template + CSS/JS files

    TODO: Check if all headfiles are available in Design site.
        This can't be done in save() method or in signals.post_save, because the related
        objects would be saved later -> It must be done in ManyRelatedManager.
        We should check if django ticked #5390 is done: 
            http://code.djangoproject.com/ticket/5390 # Add signals to ManyRelatedManager    

    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = DesignManager()

    name = models.CharField(unique=True, max_length=150, help_text="Name of this design combination",)
    template = models.CharField(max_length=128, help_text="filename of the used template for this page")
    headfiles = models.ManyToManyField("pylucid.EditableHtmlHeadFile", null=True, blank=True,
        help_text="Static files (stylesheet/javascript) for this page, included in html head via link tag"
    )
    colorscheme = models.ForeignKey(ColorScheme, null=True, blank=True)

    def save(self, *args, **kwargs):
        assert isinstance(self.template, basestring), \
            "Template must be name as a String, not a template instance!"

        return super(Design, self).save(*args, **kwargs)

    def __unicode__(self):
        sites = self.sites.values_list('name', flat=True)
        return u"Page design '%s' (on sites: %r)" % (self.name, sites)

    class Meta:
        app_label = 'pylucid'
        ordering = ("template",)
