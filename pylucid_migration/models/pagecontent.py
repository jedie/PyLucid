# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools import model_utils
from django_tools.models import UpdateInfoBaseModel

from pylucid_migration.base_models.base_models import BaseModel
from pylucid_migration.models.pagemeta import PageMeta


class PageContent(BaseModel, UpdateInfoBaseModel):
    """
    A normal CMS Page with text content.

    signals connection is in pylucid_migration.models.__init__

    inherited attributes from MarkupBaseModel:
        content field
        markup field
        get_html() method

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    content = models.TextField()
    markup = models.IntegerField()

    pagemeta = models.OneToOneField(PageMeta)

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        lang_code = self.pagemeta.language.code
        page_url = self.pagemeta.pagetree.get_absolute_url()
        return "/" + lang_code + page_url

    def get_site(self):
        return self.pagemeta.pagetree.site

    def get_name(self):
        """ Page name is optional, return PageTree slug if page name not exist """
        return self.pagemeta.name or self.pagemeta.pagetree.slug

    def get_title(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        return self.pagemeta.title or self.pagemeta.pagetree.slug

    def __unicode__(self):
        return u"PageContent %r (lang: %s, site: %s)" % (
            self.pagemeta.pagetree.slug, self.pagemeta.language.code, self.get_site().domain
        )

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'pylucid_pagecontent'
        verbose_name_plural = verbose_name = "PageContent"
        ordering = ("-lastupdatetime",)
#        ordering = ("pagetree", "language")



