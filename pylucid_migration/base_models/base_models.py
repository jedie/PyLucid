# coding: utf-8


"""
    PyLucid base models
    ~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import messages

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal


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
            messages.error(request, msg)
            domain = domain2

        absolute_url = self.get_absolute_url()
        return protocol + domain + absolute_url
    get_absolute_uri.short_description = _('absolute uri')

    class Meta:
        abstract = True






