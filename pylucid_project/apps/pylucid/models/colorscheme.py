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
from django.conf import settings

from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, AutoSiteM2M
from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.apps.pylucid.fields import ColorValueField

from pylucid_project.pylucid_plugins import update_journal



TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class ColorScheme(AutoSiteM2M, UpdateInfoBaseModel):
    """
    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
    """
    name = models.CharField(max_length=255, help_text="The name of this color scheme.")

    def update(self, colors):
        assert isinstance(colors, dict)
        new = []
        updated = []
        exists = []
        for name, value in colors.iteritems():
            color, created = Color.objects.get_or_create(
                colorscheme=self, name=name,
                defaults={"colorscheme":self, "name":name, "value":value}
            )
            if created:
                new.append(color)
            elif color.value != value:
                color.value = value
                updated.append(color)
                color.save()
            else:
                exists.append(color)
        return new, updated, exists

    def __unicode__(self):
        sites = self.sites.values_list('name', flat=True)
        return u"ColorScheme '%s' (on sites: %r)" % (self.name, sites)

    class Meta:
        app_label = 'pylucid'


class ColorManager(models.Manager):
    def get_color_dict(self, colorscheme):
        colors = self.all().filter(colorscheme=colorscheme)
        color_list = colors.values_list('name', 'value')
        return dict([(name, "#%s" % value) for name, value in color_list])

class Color(AutoSiteM2M, UpdateInfoBaseModel):
    """
    inherited attributes from AutoSiteM2M:
        sites   -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
    """
    objects = ColorManager()

    colorscheme = models.ForeignKey(ColorScheme)
    name = models.CharField(max_length=128,
        help_text="Name if this color (e.g. main_color, head_background)"
    )
    value = ColorValueField(help_text="CSS hex color value.")

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "_")
        new_name = self.name
        try:
            old_name = Color.objects.get(id=self.id).name
        except Color.DoesNotExist:
            # New color
            pass
        else:
            if new_name != old_name:
                from design import Design # import here, against import loops
                # Color name has been changed -> Rename template placeholder in every headfile, too.
                designs = Design.objects.all().filter(colorscheme=self.colorscheme)
                for design in designs:
                    headfiles = design.headfiles.all()
                    for headfile in headfiles:
                        if headfile.render != True: # File used no color placeholder
                            continue

                        old_content = headfile.content
                        # FIXME: Use flexibler regexp. for this:
                        new_content = old_content.replace("{{ %s }}" % old_name, "{{ %s }}" % new_name)
                        if old_content == new_content:
                            # content not changed?!?
                            failsafe_message(
                                "Color '{{ %s }}' not exist in headfile %r" % (old_name, headfile)
                            )
                            continue

                        if settings.DEBUG:
                            failsafe_message(
                                "change color name from '%s' to '%s' in %r" % (old_name, new_name, headfile)
                            )
                        headfile.content = new_content
                        headfile.save()

        return super(Color, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"Color '%s' #%s (%s)" % (self.name, self.value, self.colorscheme)

    class Meta:
        app_label = 'pylucid'
        unique_together = (("colorscheme", "name"),)
        ordering = ("colorscheme", "name")
