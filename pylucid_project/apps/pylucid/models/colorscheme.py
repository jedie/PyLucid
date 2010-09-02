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

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import IntegrityError
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.fields import ColorValueField
from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, AutoSiteM2M
from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from django.utils.safestring import mark_safe



TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


def slugify_colorname(value):
    """
    Normalizes string, converts, removes non-alpha characters,
    and converts spaces to "_".
    
    Based on code from: django.template.defaultfilters.slugify
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value))
    return re.sub('[-\s]+', '_', value)




class ColorScheme(AutoSiteM2M, UpdateInfoBaseModel):
    """
    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
    """
    name = models.CharField(max_length=255, help_text="The name of this color scheme.")

    def get_color_dict(self):
        querset = Color.on_site.filter(colorscheme=self)
        color_list = querset.values_list('name', 'value')
        return dict(color_list)

    def get_color_names(self):
        querset = Color.on_site.filter(colorscheme=self)
        color_list = querset.values_list('name', flat=True)
        return color_list

    def save(self, *args, **kwargs):
        super(ColorScheme, self).save(*args, **kwargs)
        from pylucid_project.apps.pylucid.models import Design # import here, against import loops
        designs = Design.objects.all().filter(colorscheme=self)
        for design in designs:
            headfiles = design.headfiles.all().filter(render=True)
            for headfile in headfiles:
                headfile.delete_cachefile(self)

    def __unicode__(self):
        sites = self.sites.values_list('name', flat=True)
        return u"ColorScheme '%s' (on sites: %r)" % (self.name, sites)

    class Meta:
        app_label = 'pylucid'



class Color(AutoSiteM2M, UpdateInfoBaseModel):
    """
    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
    """
    colorscheme = models.ForeignKey(ColorScheme)
    name = models.CharField(max_length=128,
        help_text="Name if this color (e.g. main_color, head_background)"
    )
    value = ColorValueField(help_text="CSS hex color value.")

    def clean_fields(self, exclude):
        message_dict = {}

        if "name" not in exclude:
            self.name = self.name.strip()
            test_name = slugify_colorname(self.name)
            if self.name != test_name:
                message_dict["name"] = [mark_safe(_("Name is not a slug! Use e.g.: <strong>%s</strong>") % test_name)]

        if message_dict:
            raise ValidationError(message_dict)

    def delete(self, *args, **kwargs):
        """ Check if this color is in use somewhere """
        from design import Design # import here, against import loops
        designs = Design.objects.all().filter(colorscheme=self.colorscheme)
        placeholder = u"{{ %s }}" % self.name
        for design in designs:
            headfiles = design.headfiles.all().filter(render=True)
            for headfile in headfiles:
                content = headfile.content
                if placeholder in content:
                    raise IntegrityError(
                        "Color %r can't be deleted, because it used at least in headfile %s" % (
                            self.name, headfile
                        )

                    )
        return super(Color, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if kwargs.pop("skip_renaming", False):
            # Other color was renamed in the past, we are here inner
            # renaming process, don't check renaming here, becuase we must
            # skip a closed renaming loop ;)
            super(Color, self).save(*args, **kwargs)
            return

        new_name = old_name = self.name
        try:
            old_name = Color.objects.get(id=self.id).name
        except Color.DoesNotExist:
            # New color
            pass

        if new_name != old_name:
            # Color name has been changed.
            from pylucid_project.apps.pylucid.models import Design

            changed_headfiles = []
            processed_headfiles = []
            changed_colorschemes = [self.colorscheme]

            # process every headfile witch has the same colorscheme 
            designs = Design.objects.all().filter(colorscheme=self.colorscheme)
            for design in designs:
                headfiles = design.headfiles.all().filter(render=True)
                for headfile in headfiles:
                    if headfile in processed_headfiles:
                        continue
                    processed_headfiles.append(headfile)
                    changed = headfile.rename_color(new_name, old_name)
                    if changed:
                        changed_headfiles.append(headfile)

            # process every colorscheme from the processed headfiles
            designs = Design.objects.all().exclude(colorscheme=self.colorscheme)
            for design in designs:
                colorscheme = design.colorscheme
                if colorscheme in changed_colorschemes:
                    continue
                headfiles = design.headfiles.all().filter(render=True)
                for headfile in headfiles:
                    if headfile in processed_headfiles:

                        color = Color.objects.get(colorscheme=colorscheme, name=old_name)
                        color.name = new_name
                        color.save(skip_renaming=True)

                        changed_colorschemes.append(colorscheme)
                        break

            failsafe_message(
                _(
                    'Color "%(old_name)s" renamed to "%(new_name)s":'
                    'Headfiles %(headfiles)s and colorschemes %(schemes)s updated.'
                ) % {
                    "old_name": old_name, "new_name": new_name,
                    "headfiles": ", ".join(['"%s"' % h.filepath for h in changed_headfiles]),
                    "schemes": ", ".join(['"%s"' % s.name for s in changed_colorschemes]),

                }
            )

        super(Color, self).save(*args, **kwargs)


    def __unicode__(self):
        return u"Color '%s' #%s (%s)" % (self.name, self.value, self.colorscheme)

    class Meta:
        app_label = 'pylucid'
        unique_together = (("colorscheme", "name"),)
        ordering = ("colorscheme", "name")


