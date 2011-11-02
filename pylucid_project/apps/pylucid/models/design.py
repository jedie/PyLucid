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

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template import TemplateDoesNotExist
from django.template.loader import find_template
from django.utils.translation import ugettext_lazy as _

from django_tools.models import UpdateInfoBaseModel

from pylucid_project.base_models.many2many import SiteM2M

# other PyLucid models
from colorscheme import ColorScheme


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


class DesignManager(models.Manager):
    pass

#
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
    objects = DesignManager()

    name = models.CharField(unique=True, max_length=150, help_text=_("Name of this design combination"),)
    template = models.CharField(max_length=128, help_text="filename of the used template for this page")
    headfiles = models.ManyToManyField("pylucid.EditableHtmlHeadFile", null=True, blank=True,
        help_text=_("Static files (stylesheet/javascript) for this page, included in html head via link tag")
    )
    colorscheme = models.ForeignKey(ColorScheme, null=True, blank=True)

    def clean_fields(self, exclude):
        message_dict = {}

        if "template" not in exclude:
            try:
                find_template(self.template)
            except TemplateDoesNotExist, err:
                message_dict["template"] = [_("Template doesn't exist.")]

        if message_dict:
            raise ValidationError(message_dict)

    def __unicode__(self):
        sites = self.sites.values_list('name', flat=True)
        return u"Page design '%s' (on sites: %r)" % (self.name, sites)

    class Meta:
        app_label = 'pylucid'
        ordering = ("template",)


@receiver(m2m_changed)
def design_m2m_changed_callback(sender, **kwargs):
    """
    Delete cached headfile, after design m2m saved. 
    """
    action = kwargs["action"]
    pk_set = kwargs["pk_set"]

    if action != "post_add" or not pk_set:
        return

    # Import here, against import loops
    from pylucid_project.apps.pylucid.models import EditableHtmlHeadFile

    model = kwargs["model"]
    if not model == EditableHtmlHeadFile:
        # Skip e.g. m2m to sites
        return

    for pk in pk_set:
        headfile = EditableHtmlHeadFile.objects.get(pk=pk)
        headfile.delete_all_cachefiles()
