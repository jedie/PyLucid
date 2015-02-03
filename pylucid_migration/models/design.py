# coding: utf-8


"""
    PyLucid Design model
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.core.exceptions import ValidationError
from django.db import models
from django.template import TemplateDoesNotExist
from django.template.loader import find_template, render_to_string
from django.utils.translation import ugettext_lazy as _

from django_tools.models import UpdateInfoBaseModel

from pylucid_project.base_models.many2many import SiteM2M

# other PyLucid models
from colorscheme import ColorScheme


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


class DesignManager(models.Manager):
    pass


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

    def get_headfile_data(self):
        """
        Returns all headfiles with inline compressed data
        """
        colorscheme = self.colorscheme
        headfiles = self.headfiles.all()

        inline_css_data = []
        inline_js_data = []

        for headfile in headfiles:
            headfile_type = headfile.get_type()
            inline_html = headfile.get_inline_html(colorscheme)

            if headfile_type == "css":
                inline_css_data.append(inline_html)
            elif headfile_type == "js":
                inline_js_data.append(inline_html)
            else:
                raise NotImplementedError("Datatype %r unknown!" % headfile_type)

        context = {
            "design": self,
            "colorscheme": self.colorscheme,
            "inline_css_data": inline_css_data,
            "inline_js_data": inline_js_data
        }
        headfile_data = render_to_string("pylucid/headfile_data.html", context)
        return headfile_data

    def __unicode__(self):
        sites = self.sites.values_list('name', flat=True)
        return u"Page design '%s' (on sites: %r)" % (self.name, sites)

    class Meta:
        app_label = 'pylucid'
        ordering = ("template",)
