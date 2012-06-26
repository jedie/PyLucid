# coding: utf-8


"""
    PyLucid base models
    ~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.utils.messages import failsafe_message


class SiteM2M(models.Model):
    """ Base model with sites M2M and CurrentSiteManager. """
    objects = models.Manager()
    sites = models.ManyToManyField(Site)
    on_site = CurrentSiteManager('sites')

    def __init__(self, *args, **kwargs):
        super(SiteM2M, self).__init__(*args, **kwargs)
        
        # default=[settings.SITE_ID] would be set at startup
        # This is not right if dynamic SITE_ID used
        sites_field = self._meta.get_field_by_name("sites")[0]
        sites_field.default = [settings.SITE_ID]

    def site_info(self):
        """ for admin.ModelAdmin list_display """
        sites = self.sites.all()
        return ", ".join([site.name for site in sites])
    site_info.short_description = _('Exists on site')
    site_info.allow_tags = False

    class Meta:
        abstract = True


class AutoSiteM2M(SiteM2M):
    """ Base model with sites M2M and CurrentSiteManager. """
    def save(self, *args, **kwargs):
        """
        Automatic current site, if not exist.
        
        I don't know why default=[settings.SITE_ID] is not enough, see also:
            http://www.python-forum.de/viewtopic.php?t=21022 (de)
        """
        if self.pk == None:
            # instance needs to have a primary key value before a many-to-many relationship can be used. 
            super(AutoSiteM2M, self).save(*args, **kwargs)
            if "force_insert" in kwargs:
                # we can't pass force insert to the real save method, because we
                # have save it yet.
                del kwargs["force_insert"]

        if self.sites.count() == 0:
            if settings.DEBUG:
                failsafe_message("Automatic add site id '%s' to %r" % (settings.SITE_ID, self))
            self.sites.add(settings.SITE_ID)

        super(AutoSiteM2M, self).save(*args, **kwargs)

    class Meta:
        abstract = True
