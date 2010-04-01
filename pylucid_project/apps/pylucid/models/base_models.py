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

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.managers import CurrentSiteManager

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal

from pylucid_project.utils import form_utils
from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.pylucid_plugins import update_journal


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class BaseModel(models.Model):
    def get_absolute_url(self):
        raise NotImplementedError
    get_absolute_url.short_description = _('absolute url')

    def get_site(self):
        raise NotImplementedError
    get_site.short_description = _('on site')

    def get_absolute_uri(self):
        """ returned the complete absolute URI (with the domain/host part) """
        request = ThreadLocal.get_current_request()
        is_secure = request.is_secure()
        if is_secure:
            protocol = "https://"
        else:
            protocol = "http://"
        site = self.get_site()
        domain = site.domain

        if "://" in domain:
            domain2 = domain.split("://", 1)[-1]
            msg = (
                "Wrong site domain %r: protocol should not inserted there!"
                " (Please change it to: %r)"
            ) % (domain, domain2)
            request.page_msg(msg)
            domain = domain2

        absolute_url = self.get_absolute_url()
        return protocol + domain + absolute_url
    get_absolute_uri.short_description = _('absolute uri')

    class Meta:
        abstract = True



class BaseModelManager(models.Manager):
    def easy_create(self, cleaned_form_data, extra={}):
        """
        Creating a new model instance with cleaned form data witch can hold more data than for
        this model needed.
        """
        keys = self.model._meta.get_all_field_names()
        model_kwargs = form_utils.make_kwargs(cleaned_form_data, keys)
        model_kwargs.update(extra)
        model_instance = self.model(**model_kwargs)
        model_instance.save()
        return model_instance

    def get_by_prefered_language(self, request, queryset):
        """
        return a item from queryset in this way:
         - try to get in current language
         - if not exist: try to get in system default language
         - if not exist: use the first found item
        """
        item = None
        tried_languages = []
        languages = request.PYLUCID.languages # languages are in client prefered order
        for language in languages:
            try:
                item = queryset.get(language=language)
            except ObjectDoesNotExist:
                tried_languages.append(language)
            else:
                break

        return item, tried_languages




class AutoSiteM2M(models.Model):
    """ Base model with sites M2M and CurrentSiteManager. """
    objects = models.Manager()
    sites = models.ManyToManyField(Site, default=[settings.SITE_ID])
    on_site = CurrentSiteManager('sites')

    def save(self, *args, **kwargs):
        """
        Automatic current site, if not exist.
        
        I don't know why default=[settings.SITE_ID] is not enough, see also:
            http://www.python-forum.de/topic-21022.html (de)
        """
        if self.pk == None:
            # instance needs to have a primary key value before a many-to-many relationship can be used. 
            super(AutoSiteM2M, self).save(*args, **kwargs)

        if self.sites.count() == 0:
            if settings.DEBUG:
                failsafe_message("Automatic add site id '%s' to %r" % (settings.SITE_ID, self))
            self.sites.add(settings.SITE_ID)

        super(AutoSiteM2M, self).save(*args, **kwargs)

    def site_info(self):
        """ for admin.ModelAdmin list_display """
        sites = self.sites.all()
        return ", ".join([site.name for site in sites])
    site_info.short_description = _('Exists on site')
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

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time")
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.")

    createby = models.ForeignKey(User, editable=False, related_name="%(class)s_createby",
        null=True, blank=True, # <- If the model used outsite a real request (e.g. unittest, db shell)
        help_text="User how create this entry.")
    lastupdateby = models.ForeignKey(User, editable=False, related_name="%(class)s_lastupdateby",
        null=True, blank=True, # <- If the model used outsite a real request (e.g. unittest, db shell)
        help_text="User as last edit this entry.")

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
