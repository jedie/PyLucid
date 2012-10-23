# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools import model_utils
from django_tools.models import UpdateInfoBaseModel

from pylucid_project.base_models.base_markup_model import MarkupBaseModel
from pylucid_project.base_models.base_models import BaseModelManager, BaseModel


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


class PageContentManager(BaseModelManager):
    """
    Manager class for PageContent model

    inherited from models.Manager:
        get_or_create() method, witch expected a request object as the first argument.
    """
    pass


class PageContent(BaseModel, MarkupBaseModel, UpdateInfoBaseModel):
    """
    A normal CMS Page with text content.

    signals connection is in pylucid_project.apps.pylucid.models.__init__

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
    objects = PageContentManager()

    pagemeta = models.OneToOneField("pylucid.PageMeta")

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        lang_code = self.pagemeta.language.code
        page_url = self.pagemeta.pagetree.get_absolute_url()
        return "/" + lang_code + page_url

    def get_site(self):
        return self.pagemeta.pagetree.site

    def get_update_info(self):
        """ update info for update_journal.models.UpdateJournal used by update_journal.save_receiver """
        if self.pagemeta.permitViewGroup != None or self.pagemeta.pagetree.permitViewGroup != None:
            # This entry should not be inserted in the update journal
            return None

        data = {
            "lastupdatetime": self.lastupdatetime,
            "user_name": self.lastupdateby,
            "language": self.pagemeta.language,
            "object_url": self.get_absolute_url(),
            "title": self.get_title()
        }
        return data

    def get_name(self):
        """ Page name is optional, return PageTree slug if page name not exist """
        return self.pagemeta.name or self.pagemeta.pagetree.slug

    def get_title(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        return self.pagemeta.title or self.pagemeta.pagetree.slug

    def save(self, *args, **kwargs):
        if self.pagemeta.pagetree.page_type != self.pagemeta.pagetree.PAGE_TYPE:
            # TODO: move to django model validation
            raise AssertionError("PageContent can only exist on a page type tree entry!")

        try:
            cache.smooth_update() # Save "last change" timestamp in django-tools SmoothCacheBackend
        except AttributeError:
            # No SmoothCacheBackend used -> clean the complete cache
            cache.clear()

        return super(PageContent, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"PageContent %r (lang: %s, site: %s)" % (
            self.pagemeta.pagetree.slug, self.pagemeta.language.code, self.get_site().domain
        )

    class Meta:
        app_label = 'pylucid'
        verbose_name_plural = verbose_name = "PageContent"
        ordering = ("-lastupdatetime",)
#        ordering = ("pagetree", "language")


# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PageContent)
