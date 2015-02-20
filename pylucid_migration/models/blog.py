# coding: utf-8

"""
    PyLucid blog models
    ~~~~~~~~~~~~~~~~~~~

    Database models for the blog.

    :copyleft: 2008-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib import messages
from django.core import urlresolvers
from django.core.cache import cache
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now

# http://code.google.com/p/django-tools/
from django_tools.models import UpdateInfoBaseModel

from pylucid_migration.models.language import Language


class BlogEntry(models.Model):
    """
    Language independend Blog entry.
    """
    sites = models.ManyToManyField(Site)

    is_public = models.BooleanField(
        default=True, help_text=_(
            "Is this entry is public viewable?"
            " (If not checked: Every language is non-public,"
            "  otherwise: Public only in the language, if there even set 'is public'.)"
        )
    )

    def __unicode__(self):
        return "Blog entry %i" % self.pk

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'blog_blogentry'



class BlogEntryContent(UpdateInfoBaseModel):
    """
    Language depend blog entry content.

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    content = models.TextField()
    markup = models.IntegerField()

    entry = models.ForeignKey(BlogEntry)

    language = models.ForeignKey(Language)
    headline = models.CharField(_('Headline'), max_length=255,
        help_text=_("The blog entry headline")
    )
    slug = models.SlugField(max_length=255, blank=True,
        help_text=_(
            "for url (would be set automatically from headline, if emtpy.)"
        ),
    )
    url_date = models.DateField(_('URL Date'), default=now,
        help_text=_("Date used for building the url.")
    )

    tags = models.CharField(max_length=765)
    is_public = models.BooleanField(
        default=True, help_text=_("Is entry in this language is public viewable?")
    )

    def clean_fields(self, exclude=None):
        if not self.slug:
            self.slug = slugify(self.headline)

        super(BlogEntryContent, self).clean_fields(exclude)


    def __unicode__(self):
        return self.headline

    class Meta:
        # https://docs.djangoproject.com/en/1.4/ref/models/options/#unique-together
        unique_together = (
            ("language", "url_date", "slug"),
            ("language", "url_date", "headline"),
        )
        ordering = ('-createtime', '-lastupdatetime')

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'blog_blogentrycontent'


class PylucidpluginsBlogentryTags(models.Model):
    id = models.IntegerField(primary_key=True)
    blogentry_id = models.IntegerField(unique=True)
    blogtag_id = models.IntegerField()
    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'PyLucidPlugins_blogentry_tags'

class PylucidpluginsBlogtag(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    slug = models.CharField(max_length=255, unique=True)
    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'PyLucidPlugins_blogtag'
