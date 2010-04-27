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
from django.core.cache import cache

# http://code.google.com/p/django-tools/
from django_tools import model_utils

from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, BaseModel, BaseModelManager


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


class PageContentManager(BaseModelManager):
    """
    Manager class for PageContent model

    inherited from models.Manager:
        get_or_create() method, witch expected a request object as the first argument.
    """
    pass


class PageContent(BaseModel, UpdateInfoBaseModel):
    """
    A normal CMS Page with text content.

    signals connection is in pylucid_project.apps.pylucid.models.__init__

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    # IDs used in other parts of PyLucid, too
    MARKUP_CREOLE = 6
    MARKUP_HTML = 0
    MARKUP_HTML_EDITOR = 1
    MARKUP_TINYTEXTILE = 2
    MARKUP_TEXTILE = 3
    MARKUP_MARKDOWN = 4
    MARKUP_REST = 5

    MARKUP_DATA = (
        # [0] = markup ID (e.g. database integer field)
        # [1] = lowcase, ASCII-only, no spaces (e.g. for filename)
        # [2] = verbose name (used e.g. in select input form)
        (MARKUP_CREOLE, u"creole", u'Creole wiki markup'),
        (MARKUP_HTML, u"html", u'html'),
        (MARKUP_HTML_EDITOR, u"htmleditor", u'html + JS-Editor'),
        (MARKUP_TINYTEXTILE, u"tinytextile", u'tinytextile'),
        (MARKUP_TEXTILE, u"textile", u'Textile (original)'),
        (MARKUP_MARKDOWN, u"markdown", u'Markdown'),
        (MARKUP_REST, u"rest", u'ReStructuredText'),
    )
    # For djanfo choice form field:
    MARKUP_CHOICES = [(data[0], data[2]) for data in MARKUP_DATA]

    # For easy "get name by id":
    MARKUP_DICT = dict(MARKUP_CHOICES)

    # for mapping the ID with short name
    MARKUP_SHORT_DICT = dict([(data[0], data[1]) for data in MARKUP_DATA])

    #--------------------------------------------------------------------------

    objects = PageContentManager()

    pagemeta = models.OneToOneField("pylucid.PageMeta")

    content = models.TextField(blank=True, help_text="The CMS page content.")
    markup = models.IntegerField(db_column="markup_id", max_length=1, choices=MARKUP_CHOICES)

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        lang_code = self.pagemeta.language.code
        page_url = self.pagemeta.pagetree.get_absolute_url()
        return "/" + lang_code + page_url

    def get_site(self):
        return self.pagemeta.pagetree.site

    def get_update_info(self):
        """ update info for update_journal.models.UpdateJournal used by update_journal.save_receiver """
        return {
            "lastupdatetime": self.lastupdatetime,
            "user_name": self.lastupdateby,
            "language": self.pagemeta.language,
            "object_url": self.get_absolute_url(),
            "title": self.get_title()
        }

    def get_name(self):
        """ Page name is optional, return PageTree slug if page name not exist """
        return self.pagemeta.name or self.pagemeta.pagetree.slug

    def get_title(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        return self.pagemeta.title or self.pagemeta.pagetree.slug

    def save(self, *args, **kwargs):
        if self.pagemeta.pagetree.page_type != self.pagemeta.pagetree.PAGE_TYPE:
            # FIXME: Better error with django model validation?
            raise AssertionError("PageContent can only exist on a page type tree entry!")
        cache.clear() # FIXME: This cleaned the complete cache for every site!
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


