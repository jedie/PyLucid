# coding: utf-8

"""
    PyLucid auto model info
    ~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__ = "$Rev:$"

import sys
import warnings

from django.db import models
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import transaction, IntegrityError
from pylucid.shortcuts import user_message_or_warn
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.managers import CurrentSiteManager

from django_tools.middlewares import ThreadLocal


class AutoSiteM2M(models.Model):
    """
    Add site and on_site to model, and add at least the current site in save method.
    """
    site = models.ManyToManyField(Site)
    on_site = CurrentSiteManager()

    def save(self, *args, **kwargs):
        """ Automatic current site, if not exist. """
        if self.pk == None:
            # instance needs to have a primary key value before a many-to-many relationship can be used.
            super(AutoSiteM2M, self).save(*args, **kwargs)

        if self.site.count() == 0:
            site = Site.objects.get_current()
            if settings.DEBUG:
                user_message_or_warn("Automatic add site '%s' to %r" % (site.name, self))
            self.site.add(site)

        super(AutoSiteM2M, self).save(*args, **kwargs)

    def site_info(self):
        """ for admin.ModelAdmin list_display """
        sites = self.site.all()
        return ", ".join([site.name for site in sites])
    site_info.short_description = _('on sites')
    site_info.allow_tags = False

    class Meta:
        abstract = True


class UpdateInfoBaseModel(models.Model):
    """
    Base model with update info attributes, used by many models.
    The createby and lastupdateby ForeignKey would be automaticly updated. This needs the 
    request object as the first argument in the save method.
    """
    objects = models.Manager()

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)

    createby = models.ForeignKey(User, editable=False, related_name="%(class)s_createby",
        null=True, blank=True, # <- If the model used outsite a real request (e.g. unittest, db shell)
        help_text="User how create the current page.",)
    lastupdateby = models.ForeignKey(User, editable=False, related_name="%(class)s_lastupdateby",
        null=True, blank=True, # <- If the model used outsite a real request (e.g. unittest, db shell)
        help_text="User as last edit the current page.",)

    def save(self, *args, **kwargs):
        """
        Automatic update createby and lastupdateby attributes with the request object witch must be
        the first argument.
        """
        current_user = ThreadLocal.get_current_user()

        if current_user and isinstance(current_user, User):
            if self.pk == None or kwargs.get("force_insert", False): # New model entry
                self.createby = current_user
            self.lastupdateby = current_user

        return super(UpdateInfoBaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
